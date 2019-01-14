from __future__ import unicode_literals

import os
import re
import sys
import traceback

from traitlets import Unicode
from subprocess import check_output
from uuid import uuid4
from ipykernel.kernelbase import Kernel
from .coqtop import CoqtopWrapper

__version__ = '1.3.0'


LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')

ROLLBACK_COMM_TARGET_NAME = "coq_kernel.rollback_comm"

with open(os.path.join(os.path.dirname(__file__), "rollback_comm.js"), 'r') as f:
    HTML_ROLLBACK_COMM_DEFINITION = """<script>{}</script>""".format(f.read())

HTML_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-check fa text-success"></i>
    <span>{2}</span>
</div>
"""

HTML_ERROR_OUTPUT_TEMPLATE = """
<div id="output_{0}">
    <pre>{1}</pre>
    <br>
    <i class="fa-times fa text-danger"></i>
    <span>{2}</span>
</div>
"""

HTML_ROLLBACK_MESSAGE_TEMPLATE = """
<div id="rollback_message_{0}" style="display: none">
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLLBACK_MESSAGE = """
<div>
    <i class="fa-exclamation-circle fa text-info"></i>
    <span>Cell rolled back.</span>
</div>
"""

HTML_ROLLBACK_BUTTON_TEMPLATE = """
<div style="position: relative;">
    <button id="rollblack_button_{0}" class="btn btn-default btn-xs" style="display: none; margin-top: 5px;" onclick="coq_kernel_rollback_comm_{0}.rollback()">
        <i class="fa-step-backward fa"></i>
        <span class="toolbar-btn-label">Rollback cell</span>
    </button>
</div>
"""

HTML_ROLLBACK_COMM_INIT_TEMPLATE = """
<script>
    var coq_kernel_rollback_comm_{0} = new CoqKernelRollbackComm('{0}');
    coq_kernel_rollback_comm_{0}.init();
</script>
"""


class CellRecord:

    def __init__(self, state_label_before, state_label_after, display_id, rolled_back, parent_header):
        self.state_label_before = state_label_before
        self.state_label_after = state_label_after
        self.display_id = display_id
        self.rolled_back = rolled_back
        self.parent_header = parent_header

class CellJournal:

    def __init__(self, kernel):
        self.log = kernel.log # TODO
        self.history = []

    def add(self, state_label_before, state_label_after, display_id, rolled_back, parent_header):
        self.history.append(CellRecord(state_label_before, state_label_after, display_id, rolled_back, parent_header))

    def find_by_display_id(self, display_id):
        result = list(filter(lambda r: r.display_id == display_id, self.history))
        if len(result) == 1:
            return result[0]
        else:
            return None

    def find_affected_by_roll_back(self, state_label_before):
        return list(filter(lambda r: int(r.state_label_before) > int(state_label_before) and not r.rolled_back, self.history))

class CoqKernel(Kernel):
    implementation = 'coq'
    implementation_version = __version__
    language = 'coq'

    @property
    def language_info(self):
        return {
            'name': 'coq',
            'mimetype': 'text/x-coq',
            'file_extension': '.v',
            'version': self.language_version
        }

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['coqtop', '--version']).decode('utf-8')
        return self._banner

    @property
    def language_version(self):
        return LANGUAGE_VERSION_PATTERN.search(self.banner).group(1)


    coqtop_args = Unicode().tag(config=True)


    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._coqtop = CoqtopWrapper(self, self.coqtop_args)
        self._journal = CellJournal(self)
        self._comms = {}
        for msg_type in ['comm_open', 'comm_msg', 'comm_close']:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            self.log.info("Processing 'execute_request', code: \n{}\n".format(repr(code)))
            if code.strip("\n\r\t ") != "":

                result = self._coqtop.eval(code)
                (raw_outputs, footer_message, rolled_back, state_label_before, state_label_after) = result
                display_id = str(uuid4()).replace("-", "")

                self._journal.add(state_label_before, state_label_after, display_id, rolled_back, self._parent_header)

                self.log.info("Sending 'execute_result', evaluation result: \n{}\n".format(repr(result)))
                self._send_execute_result(raw_outputs, footer_message, display_id, rolled_back)
            else:
                self.log.info("code is empty - skipping evaluation and sending results.")

            return self._build_ok_content()
        except Exception as e:
            self.log.exception("Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(*sys.exc_info())

    def comm_open(self, stream, ident, msg):
        content = msg["content"]
        if content["target_name"] == ROLLBACK_COMM_TARGET_NAME:
            self._comms[content["comm_id"]] = content["data"]["display_id"]
            self.log.info("Comm opened, msg: {}".format(repr(msg)))
        else:
            self.log.error("Unexpected comm_open, msg: {}".format(repr(msg)))

    def comm_msg(self, stream, ident, msg):
        content = msg["content"]
        comm_id = content["comm_id"]
        if comm_id in self._comms:
            if content["data"]["comm_msg_type"] == "request_rollback_sate":
                self._handle_request_rollback_sate(comm_id, msg)
            elif content["data"]["comm_msg_type"] == "rollback":
                self._handle_rollback(msg)
            else:
                self.log.error("Unexpected comm_msg, msg: {}".format(repr(msg)))
        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))

    def comm_close(self, stream, ident, msg):
        del self._comms[msg["content"]["comm_id"]]
        self.log.info("Comm closed, msg: {}".format(repr(msg)))

    def _handle_request_rollback_sate(self, comm_id, msg):
        cell_record = self._journal.find_by_display_id(self._comms[comm_id])
        if cell_record is not None:
            self._send_rollback_state_comm_msg(comm_id, cell_record.rolled_back)
        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))

    def _handle_rollback(self, msg):
        self.log.info("rollback, msg: {}".format(repr(msg)))
        comm_id = msg["content"]["comm_id"]
        display_id = self._comms[comm_id]
        cell_record = self._journal.find_by_display_id(display_id)

        if cell_record is not None and not cell_record.rolled_back:
            self._coqtop.eval("BackTo {}.".format(cell_record.state_label_before)) # TODO check for error?

            for record in [cell_record] + self._journal.find_affected_by_roll_back(cell_record.state_label_before):
                # mark cell as rolled back
                record.rolled_back= True

                # update content of rolled back cell
                self._send_rollback_update_display_data(record.display_id, record.parent_header)

                # notify any relevant rollback comms
                for comm_id in [c for (c, d) in self._comms.items() if d == record.display_id]:
                    self._send_rollback_state_comm_msg(comm_id, True)

        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))


    def _build_ok_content(self):
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def _build_error_content(self, ex_type, ex, tb):
        return {
            'status': 'error',
            'ename' : ex_type.__name__,
            'evalue' : repr(ex),
            'traceback' : traceback.format_list(traceback.extract_tb(tb))
        }

    def _build_display_data_content(self, text, html, display_id):
        return {
            'data': { 'text/plain': text, 'text/html': html },
            'metadata': {},
            'transient': { 'display_id': display_id }
        }

    def _send_rollback_state_comm_msg(self, comm_id, rolled_back):
        content = {
            "comm_id": comm_id,
            "data": {
                "comm_msg_type": "rollback_state",
                "rolled_back": rolled_back
            }
        }
        self.session.send(self.iopub_socket, "comm_msg", content, None, None, None, None, None, None)

    def _send_rollback_update_display_data(self, display_id, parent_header):
        text = "Cell rolled back."
        content = self._build_display_data_content(text, HTML_ROLLBACK_MESSAGE, display_id)
        self.session.send(self.iopub_socket, "update_display_data", content, parent_header, None, None, None, None, None)

    def _send_execute_result(self, raw_outputs, footer_message, display_id, rolled_back):
        text = self._render_text_result(raw_outputs, footer_message)
        html = self._render_html_result(raw_outputs, footer_message, display_id, not rolled_back)
        content = self._build_display_data_content(text, html, display_id)
        content['execution_count'] = self.execution_count
        self.send_response(self.iopub_socket, 'execute_result', content)

    def _render_text_result(self, raw_outputs, footer_message):
        cell_output = "\n".join(raw_outputs)
        cell_output = cell_output.rstrip("\n\r\t ").lstrip("\n\r")

        # strip extra tag formating
        # TODO this is a temporary solution that won't be relevant after implementing ide xml protocol
        for tag in ["warning", "infomsg"]:
            cell_output = cell_output.replace("<{}>".format(tag), "").replace("</{}>".format(tag), "")

        if footer_message is not None:
            cell_output += "\n\n" + footer_message

        return cell_output

    def _render_html_result(self, raw_outputs, footer_message, display_id, success_output):
        if success_output:
            html = HTML_OUTPUT_TEMPLATE.format(display_id, self._render_text_result(raw_outputs, None), footer_message)
            html += HTML_ROLLBACK_MESSAGE_TEMPLATE.format(display_id)
            html += HTML_ROLLBACK_BUTTON_TEMPLATE.format(display_id)
            html += HTML_ROLLBACK_COMM_DEFINITION
            html += HTML_ROLLBACK_COMM_INIT_TEMPLATE.format(display_id)
        else:
            html = HTML_ERROR_OUTPUT_TEMPLATE.format(display_id, self._render_text_result(raw_outputs, None), footer_message)

        return html


# This entry point is used for debug only:
if __name__ == '__main__':
    from sys import argv
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
