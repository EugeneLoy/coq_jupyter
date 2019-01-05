import pexpect
import re
import random

from ipykernel.kernelbase import Kernel
from subprocess import check_output
from operator import itemgetter

__version__ = '1.1.0'

PROMPT = u"\<prompt\>.+?\s\<\s(?P<state_label>\d+)\s\|(?P<proving>.*?)\|\s\d+\s\<\s\<\/prompt\>"

LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')
ANSI_ESCAPE_PATTERN = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]') # see: https://stackoverflow.com/a/38662876/576549


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

    _state_labbel = None

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_coqtop()

    def _start_coqtop(self):
        self._coqtop = pexpect.spawn(u"coqtop -emacs -quiet", echo=False, encoding=u"utf-8")
        self._state_labbel = "1"
        self._eval(u"(* dummy init command *)")

    def _eval(self, code):
        rollback_state_label = self._state_labbel
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

            return self._render_cell_output(raw_outputs, footer_message)

        # rollback issued hidden commands
        # TODO not 100% sure if this rollback is really needed. Leave it for now.
        self._coqtop.sendline(u"BackTo {}.".format(outputs[-hidden_commands_issued][0].group(u"state_label")))
        self._expect_coqtop_prompt()

        # treat state after hidden commands rollback as 'commited'
        self._state_labbel = self._coqtop.match.group(u"state_label")

        # build cell output message
        raw_outputs = list(map(itemgetter(1), outputs))
        del raw_outputs[-hidden_commands_issued] # omit checkpoint marker output

        if self._coqtop.match.group(u"proving") != u"":
            footer_message = u"Proving: {}".format(self._coqtop.match.group(u"proving"))
        else:
            footer_message = None

        return self._render_cell_output(raw_outputs, footer_message)

    def _render_cell_output(self, raw_outputs, footer_message):
        cell_output = u"\n".join(raw_outputs)
        cell_output = cell_output.rstrip(u"\n\r\t ").lstrip(u"\n\r")

        if footer_message is not None:
            cell_output += "\n\n" + footer_message

        return cell_output

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

    def _send_execute_result(self, text):
        self.send_response(self.iopub_socket, 'execute_result', {
            'data': { 'text/plain': text },
            'metadata': {},
            'execution_count': self.execution_count
        })

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            self.log.info(u"Processing 'execute_request', code: \n{}\n".format(repr(code)))
            if code.strip(u"\n\r\t ") != u"":
                result = self._eval(code)
                self.log.info(u"Sending 'execute_result', evaluation result: \n{}\n".format(repr(result)))
                self._send_execute_result(result)
            else:
                self.log.info(u"code is empty - skipping evaluation and sending results.")

            return self._build_ok_content()
        except Exception as e:
            self.log.exception(u"Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(e)

# This entry point is used for debug only:
if __name__ == '__main__':
    from sys import argv
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
