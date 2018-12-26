import pexpect
import re

from ipykernel.kernelbase import Kernel
from subprocess import check_output


__version__ = '1.0.0'

INITIAL_PROMPT = u".*Coq\s\<\s"
PROMPT = u"([^\s]+)\s\<\s" # TODO add match for newline here

LANGUAGE_VERSION_PATTERN = re.compile(r'version (\d+(\.\d+)+)')


class CoqKernel(Kernel):
    # TODO tweak the following fields:
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


    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            result = self._eval(code)

            self.send_response(self.iopub_socket, 'execute_result', {
                'data': { 'text/plain': result },
                'metadata': {},
                'execution_count': self.execution_count # TODO check if this belongs here
            })

            return {
                'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
            }
        except Exception as e:
            return {
                'status': 'abort',
                'execution_count': self.execution_count
            }

# This entry point is used for debug only:
if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel)
