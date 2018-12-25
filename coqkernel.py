import pexpect

from ipykernel.kernelbase import Kernel

INITIAL_PROMPT = ".*Coq\s\<\s"
PROMPT = "[^\s]+\s\<\s" # TODO add match for newline here

class CoqKernel(Kernel):
    # TODO tweak the following fields:
    implementation = 'Coq'
    implementation_version = '1.0'
    language = 'coq'
    language_version = '1.0'
    language_info = {
        'name': 'coq',
        'mimetype': 'text/coq',
        'file_extension': '.v',
    }
    banner = "Coq kernel"

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

        return u"\n".join(outputs);

        # TODO cleanup:
        # self._coqtop.sendline(u" ".join(code.splitlines()))
        # self._coqtop.expect("[^\s]+\s\<\s", None)
        # return self._coqtop.before


    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        try:
            result = self._eval(code)

            stream_content = {
                'name': 'stdout',
                'text': result
            }
            self.send_response(self.iopub_socket, 'stream', stream_content)

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


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel)
