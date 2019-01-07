import pexpect
import re
import random

from ipykernel.kernelbase import Kernel
from subprocess import check_output
from operator import itemgetter
from uuid import uuid4

__version__ = '1.2.0'

PROMPT = u"\<prompt\>.+?\s\<\s(?P<state_label>\d+)\s\|(?P<proving>.*?)\|\s\d+\s\<\s\<\/prompt\>"

LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')
ANSI_ESCAPE_PATTERN = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]') # see: https://stackoverflow.com/a/38662876/576549

ROLLBACK_COMM_TARGET_NAME = "coq_kernel.rollback_comm"

# TODO decide, maybe move this to more appropriate place:
HTML_COMM_DEFINITION = """
function CoqKernelRollbackComm(display_id) {
    var self = this;
    self.display_id = display_id;
    self.button_id = "#rollblack_button_" + self.display_id;
    self.jupyter = require('base/js/namespace');

    self.init = function () {
        if (self.jupyter.notebook.kernel !== null) {
            console.info('Initializing rollback comm for: ' + self.display_id);
            self.comm = self.jupyter.notebook.kernel.comm_manager.new_comm('coq_kernel.rollback_comm', { 'display_id': self.display_id });
            self.comm.on_msg(self.handle_comm_message);
            self.comm.send({ 'comm_msg_type': 'request_rollback_sate' });
        } else {
            // kernel is not ready yet - try later
            setTimeout(self.init, 1000)
        }
    };

    self.rollback = function () {
        self.comm.send({ 'comm_msg_type': 'rollback' });
        $(self.button_id).prop('disabled', true);
    };

    self.handle_comm_message = function(msg) {
        if (msg.content.data.comm_msg_type === "rollback_state") {
            $(self.button_id).toggle(!msg.content.data.rolled_back)
        } else {
            console.error('Unexpected comm message: ' + JSON.stringify(msg));
        }
    }
};
"""
HTML_OUTPUT_TEMPLATE = """<pre>{}</pre>"""
HTML_ROLLBACK_BUTTON_TEMPLATE = """<button id="rollblack_button_{0}" style="display: none" onclick="coq_kernel_rollback_comm_{0}.rollback()">Rollback cell</button>"""
HTML_ROLLBACK_COMM_INIT_TEMPLATE = """<script>{0} var coq_kernel_rollback_comm_{1} = new CoqKernelRollbackComm('{1}'); coq_kernel_rollback_comm_{1}.init();</script>"""


class CoqtopWrapper:

    state_label = None

    def __init__(self, kernel):
        self.log = kernel.log # TODO
        self._coqtop = pexpect.spawn(u"coqtop -emacs -quiet", echo=False, encoding=u"utf-8")
        self.state_label = "1"
        self.eval(u"(* dummy init command *)")

    def eval(self, code):
        rollback_state_label = self.state_label
        checkpoint_marker_lhs = random.randint(0, 499)
        checkpoint_marker_rhs = random.randint(0, 499)
        checkpoint_marker = str(checkpoint_marker_lhs + checkpoint_marker_rhs)
        eval_checkpoint_command = u"Compute {} + {}.".format(checkpoint_marker_lhs, checkpoint_marker_rhs)
        hidden_commands_issued = 1

        # attempt evaluation
        self._coqtop.send(u"{}\n{}\n".format(code, eval_checkpoint_command))

        # collect evaluation output
        outputs = []
        while True:
            (prompt_match, raw_output, simplified_output, error_message) = self._expect_coqtop_prompt()
            outputs.append((prompt_match, raw_output, simplified_output, error_message))

            if checkpoint_marker in simplified_output:
                self.log.debug(u"checkpoint reached")
                break

            if error_message and eval_checkpoint_command in simplified_output:
                self.log.debug(u"checkpoint eval failed")
                break

        # query proof state if proving something now
        if outputs[-1][0].group(u"proving") != u"":
            self._coqtop.sendline(u"Show.")
            outputs.append(self._expect_coqtop_prompt())
            hidden_commands_issued += 1

        # do full cell rollback if error were detected
        if any(map(itemgetter(3), outputs)):
            self._coqtop.sendline(u"BackTo {}.".format(rollback_state_label))
            self._expect_coqtop_prompt()

            raw_outputs = []
            footer_message = "Cell evaluation error: some of the commands resulted in error. Cell rolled back."
            for (_, raw_output, simplified_output, _) in outputs:
                if eval_checkpoint_command in simplified_output:
                    footer_message = "Cell evaluation error: last cell command is incomplete or malformed. Cell rolled back."
                    break

                if checkpoint_marker in simplified_output:
                    break

                raw_outputs.append(simplified_output)

            return (raw_outputs, footer_message, True)

        # rollback issued hidden commands
        # TODO not 100% sure if this rollback is really needed. Leave it for now.
        self._coqtop.sendline(u"BackTo {}.".format(outputs[-hidden_commands_issued][0].group(u"state_label")))
        self._expect_coqtop_prompt()

        # treat state after hidden commands rollback as 'commited'
        self.state_label = self._coqtop.match.group(u"state_label")

        # build cell output message
        raw_outputs = list(map(itemgetter(1), outputs))
        del raw_outputs[-hidden_commands_issued] # omit checkpoint marker output

        if self._coqtop.match.group(u"proving") != u"":
            footer_message = u"Proving: {}".format(self._coqtop.match.group(u"proving"))
        else:
            footer_message = None

        return (raw_outputs, footer_message, False)

    def _expect_coqtop_prompt(self):
        self.log.debug(u"expecting coqtop prompt")
        self._coqtop.expect(PROMPT, None)

        prompt_match = self._coqtop.match
        self.log.debug(u"coqtop prompt: {}".format(repr(prompt_match)))

        raw_output = self._coqtop.before
        self.log.debug(u"coqtop output (raw): {}".format(repr(raw_output)))

        simplified_output = self._simplify_output(raw_output)
        self.log.debug(u"coqtop output (simplified): {}".format(repr(simplified_output)))

        error_message = self._is_error_output(simplified_output)
        self.log.debug(u"coqtop output contains error message: {}".format(error_message))

        return (prompt_match, raw_output, simplified_output, error_message)

    def _simplify_output(self, output):
        # clean colors
        output = ANSI_ESCAPE_PATTERN.sub(u"", output)
        # replace \n\r with \n
        output = u"\n".join(output.splitlines())
        return output.strip(u"\n\t ")

    def _is_error_output(self, output):
        lines = output.splitlines()

        if len(lines) == 0:
            return False

        error_location_found = False
        for line in lines:
            error_location_found = error_location_found or line.startswith("Toplevel input, characters")
            if error_location_found and (line.startswith("Error:") or line.startswith("Syntax error:")):
                return True

        return False

class CellJournal:

    def __init__(self, kernel):
        self.log = kernel.log # TODO
        self.history = []

    def add(self, state_label_before, state_label_after, display_id, rolled_back, parent_header):
        self.history.append([state_label_before, state_label_after, display_id, rolled_back, parent_header])

    def find_by_display_id(self, display_id):
        result = list(filter(lambda r: r[2] == display_id and not r[3], self.history))
        if len(result) == 1:
            return result[0]
        else:
            return None

    def find_rolled_back(self, state_label_before):
        return list(filter(lambda r: int(r[0]) > int(state_label_before) and not r[3], self.history))

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


    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._coqtop = CoqtopWrapper(self)
        self._journal = CellJournal(self)
        self._comms = {}
        for msg_type in ['comm_open', 'comm_msg', 'comm_close']:
            self.shell_handlers[msg_type] = getattr(self, msg_type)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            self.log.info(u"Processing 'execute_request', code: \n{}\n".format(repr(code)))
            if code.strip(u"\n\r\t ") != u"":

                state_label_before = self._coqtop.state_label
                result = self._coqtop.eval(code)
                (raw_outputs, footer_message, rolled_back) = result
                state_label_after = self._coqtop.state_label
                display_id = str(uuid4()).replace("-", "")

                self._journal.add(state_label_before, state_label_after, display_id, rolled_back, self._parent_header)

                self.log.info(u"Sending 'execute_result', evaluation result: \n{}\n".format(repr(result)))
                self._send_execute_result(raw_outputs, footer_message, display_id, rolled_back)
            else:
                self.log.info(u"code is empty - skipping evaluation and sending results.")

            return self._build_ok_content()
        except Exception as e:
            self.log.exception(u"Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(e)

    def comm_open(self, stream, ident, msg):
        content = msg["content"]
        if content["target_name"] == ROLLBACK_COMM_TARGET_NAME:
            self._comms[content["comm_id"]] = content["data"]["display_id"]
            self.log.info(u"Comm opened, msg: {}".format(repr(msg)))
        else:
            self.log.error(u"Unexpected comm_open, msg: {}".format(repr(msg)))

    def comm_msg(self, stream, ident, msg):
        content = msg["content"]
        comm_id = content["comm_id"]
        if comm_id in self._comms:
            if content["data"]["comm_msg_type"] == "request_rollback_sate":
                self._send_rollback_state_comm_msg(comm_id, False)
            elif content["data"]["comm_msg_type"] == "rollback":
                self._handle_rollback(msg)
            else:
                self.log.error(u"Unexpected comm_msg, msg: {}".format(repr(msg)))
        else:
            self.log.info(u"Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))

    def comm_close(self, stream, ident, msg):
        del self._comms[msg["content"]["comm_id"]]
        self.log.info(u"Comm closed, msg: {}".format(repr(msg)))

    def _handle_rollback(self, msg):
        self.log.info(u"rollback, msg: {}".format(repr(msg)))
        comm_id = msg["content"]["comm_id"]
        display_id = self._comms[comm_id]
        cell_record = self._journal.find_by_display_id(display_id)

        if cell_record is not None:
            state_label_before = cell_record[0]
            self._coqtop.eval("BackTo {}.".format(state_label_before)) # TODO check for error?

            for record in [cell_record] + self._journal.find_rolled_back(state_label_before):
                record[3] = True
                self._send_rollback_update_display_data(record[2], record[4])

        else:
            self.log.info(u"Unexpected (possibly leftover) comm_msg, msg: {}".format(repr(msg)))


    def _build_ok_content(self):
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

    def _build_error_content(self, e):
        return {
            'status': 'error',
            'ename' : type(e).__name__,
            'evalue' : repr(e), #TODO
            'traceback' : [] # TODO
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
        html = "<pre>Cell rolled back.</pre>"
        content = self._build_display_data_content(text, html, display_id)
        self.session.send(self.iopub_socket, "update_display_data", content, parent_header, None, None, None, None, None)

    def _send_execute_result(self, raw_outputs, footer_message, display_id, rolled_back):
        text = self._render_text_result(raw_outputs, footer_message)
        html = self._render_html_result(raw_outputs, footer_message, display_id)
        content = self._build_display_data_content(text, html, display_id)
        content['execution_count'] = self.execution_count
        self.send_response(self.iopub_socket, 'execute_result', content)

    def _render_text_result(self, raw_outputs, footer_message):
        cell_output = u"\n".join(raw_outputs)
        cell_output = cell_output.rstrip(u"\n\r\t ").lstrip(u"\n\r")

        if footer_message is not None:
            cell_output += "\n\n" + footer_message

        return cell_output

    def _render_html_result(self, raw_outputs, footer_message, display_id):
        html = HTML_OUTPUT_TEMPLATE.format(self._render_text_result(raw_outputs, footer_message))
        html += HTML_ROLLBACK_BUTTON_TEMPLATE.format(display_id)
        html += HTML_ROLLBACK_COMM_INIT_TEMPLATE.format(HTML_COMM_DEFINITION, display_id)
        return html


# This entry point is used for debug only:
if __name__ == '__main__':
    from sys import argv
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
