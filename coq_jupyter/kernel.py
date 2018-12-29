import pexpect
import re

from ipykernel.kernelbase import Kernel
from subprocess import check_output


__version__ = '1.0.0'

INITIAL_PROMPT = u".*Coq\s\<\s"
PROMPT = u"([^\s]+)\s\<\s" # TODO add match for newline here

LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')


class CoqKernel(Kernel):
    implementation = 'coq'
    implementation_version = __version__
    language = 'coq'

    @property
    def language_info(self):
        return {
            'name': 'coq',
            'mimetype': 'text/coq',
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
        self._start_coqtop()

    def _start_coqtop(self):
        self._coqtop = pexpect.spawn('coqtop', echo=False, encoding='utf-8')
        self._coqtop.expect(INITIAL_PROMPT, None)

    def _eval(self, code):
        lines = [line for line in code.splitlines() if line.strip("\n\r\t ") != u""]
        outputs = []
        for line in lines:
            self._coqtop.sendline(line)
            self._coqtop.expect(PROMPT, None)
            outputs.append(self._coqtop.before);

        # Parse "proving" context from prompt
        prompt_context = self._coqtop.match.group(1)
        if prompt_context != u"Coq":
            outputs.append(u"Proving: {}".format(prompt_context))

        return u"\n".join(outputs);

        # TODO cleanup:
        # self._coqtop.sendline(u" ".join(code.splitlines()))
        # self._coqtop.expect("[^\s]+\s\<\s", None)
        # return self._coqtop.before

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
            self.log.info("Processing 'execute_request', code: \n{}\n".format(repr(code)))
            result = self._eval(code)
            self.log.info("Sending 'execute_result', evaluation result: \n{}\n".format(repr(result)))
            self._send_execute_result(result)
            return self._build_ok_content()
        except Exception as e:
            self.log.exception("Error during evaluating code: \n'{}'\n".format(repr(code)))
            return self._build_error_content(e)

# This entry point is used for debug only:
if __name__ == '__main__':
    from sys import argv
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
