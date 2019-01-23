from __future__ import unicode_literals

import re
import sys
import traceback
import time

from traitlets import Unicode
from subprocess import check_output
from uuid import uuid4
from ipykernel.kernelbase import Kernel
from .coqtop import CoqtopWrapper, CoqtopError
from .renderer import Renderer, HTML_ROLL_BACK_MESSAGE, TEXT_ROLL_BACK_MESSAGE


__version__ = '1.3.0'


LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')

CELL_COMM_TARGET_NAME = "coq_kernel.cell_comm"


class CellRecord:

    def __init__(self, state_label_before, evaluated, rolled_back, display_id, parent_header):
        self.state_label_before = state_label_before
        self.evaluated = evaluated
        self.rolled_back = rolled_back
        self.display_id = display_id
        self.parent_header = parent_header


class CellJournal:

    def __init__(self, kernel):
        self.log = kernel.log # TODO
        self.history = []

    def add(self, state_label_before, evaluated, rolled_back, display_id, parent_header):
        self.history.append(CellRecord(state_label_before, evaluated, rolled_back, display_id, parent_header))

    def find_by_display_id(self, display_id):
        result = list(filter(lambda r: r.display_id == display_id, self.history))
        if len(result) == 1:
            return result[0]
        else:
            return None

    def find_rolled_back_transitively(self, state_label_before):
        return list(filter(lambda r: int(r.state_label_before) > int(state_label_before) and not r.rolled_back, self.history))


def shutdown_on_coqtop_error(function):
    def wrapper(self, *args, **kwargs):
        try:
            return function(self, *args, **kwargs)
        except CoqtopError:
            self.log.exception("CoqtopError has occured. Scheduling shutdown.")
            from tornado import ioloop
            loop = ioloop.IOLoop.current()
            loop.add_timeout(time.time() + 0.1, loop.stop)
            raise

    return wrapper


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


    @shutdown_on_coqtop_error
    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._coqtop = CoqtopWrapper(self, self.coqtop_args)
        self._journal = CellJournal(self)
        self._renderer = Renderer()
        self._comms = {}
        for msg_type in ['comm_open', 'comm_msg', 'comm_close']:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            self.log.info("Processing 'execute_request', code: \n{}\n".format(repr(code)))
            if code.strip("\n\r\t ") != "":

                result = shutdown_on_coqtop_error(lambda self: self._coqtop.eval(code))(self)
                (state_label_before, evaluated, outputs) = result
                display_id = str(uuid4()).replace("-", "")
                self._journal.add(state_label_before, evaluated, False, display_id, self._parent_header)

                if not silent:
                    self.log.info("Sending 'execute_result', evaluation result: \n{}\n".format(repr(result)))
                    self._send_execute_result(outputs, display_id, evaluated)
            else:
                self.log.info("code is empty - skipping evaluation and sending results.")

            return self._build_ok_content()
        except Exception as e:
            self.log.exception("Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(*sys.exc_info())

    def comm_open(self, stream, ident, msg):
        content = msg["content"]
        if content["target_name"] == CELL_COMM_TARGET_NAME:
            self._comms[content["comm_id"]] = content["data"]["display_id"]
            self.log.info("Comm opened, msg: {}".format(repr(msg)))
        else:
            self.log.error("Unexpected comm_open, msg: {}".format(repr(msg)))

    @shutdown_on_coqtop_error
    def comm_msg(self, stream, ident, msg):
        content = msg["content"]
        comm_id = content["comm_id"]
        if comm_id in self._comms:
            if content["data"]["comm_msg_type"] == "request_cell_sate":
                self._handle_request_cell_sate(comm_id, msg)
            elif content["data"]["comm_msg_type"] == "roll_back":
                self._handle_roll_back(msg)
            else:
                self.log.error("Unexpected comm_msg, msg: {}".format(repr(msg)))
        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))

    def comm_close(self, stream, ident, msg):
        del self._comms[msg["content"]["comm_id"]]
        self.log.info("Comm closed, msg: {}".format(repr(msg)))

    def _handle_request_cell_sate(self, comm_id, msg):
        cell_record = self._journal.find_by_display_id(self._comms[comm_id])
        if cell_record is not None:
            self._send_cell_state_comm_msg(comm_id, cell_record.evaluated, cell_record.rolled_back)
        else:
            self.log.info("Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))

    def _handle_roll_back(self, msg):
        self.log.info("roll back, msg: {}".format(repr(msg)))
        comm_id = msg["content"]["comm_id"]
        display_id = self._comms[comm_id]
        cell_record = self._journal.find_by_display_id(display_id)

        if cell_record is not None and not cell_record.rolled_back:
            self._coqtop.roll_back_to(cell_record.state_label_before)

            for record in [cell_record] + self._journal.find_rolled_back_transitively(cell_record.state_label_before):
                # mark cell as rolled back
                record.rolled_back= True

                # update content of rolled back cell
                self._send_roll_back_update_display_data(record.display_id, record.parent_header)

                # notify any relevant cell comms
                for comm_id in [c for (c, d) in self._comms.items() if d == record.display_id]:
                    self._send_cell_state_comm_msg(comm_id, record.evaluated, record.rolled_back)

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

    def _send_cell_state_comm_msg(self, comm_id, evaluated, rolled_back):
        content = {
            "comm_id": comm_id,
            "data": {
                "comm_msg_type": "cell_state",
                "evaluated": evaluated,
                "rolled_back": rolled_back
            }
        }
        self.session.send(self.iopub_socket, "comm_msg", content, None, None, None, None, None, None)

    def _send_roll_back_update_display_data(self, display_id, parent_header):
        content = self._build_display_data_content(TEXT_ROLL_BACK_MESSAGE, HTML_ROLL_BACK_MESSAGE, display_id)
        self.session.send(self.iopub_socket, "update_display_data", content, parent_header, None, None, None, None, None)

    def _send_execute_result(self, outputs, display_id, evaluated):
        text = self._renderer.render_text_result(outputs)
        html = self._renderer.render_html_result(outputs, display_id, evaluated)
        content = self._build_display_data_content(text, html, display_id)
        content['execution_count'] = self.execution_count
        self.send_response(self.iopub_socket, 'execute_result', content)
