from ipykernel.kernelbase import Kernel

class CoqKernel(Kernel):
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

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        if not silent:
            stream_content = {'name': 'stdout', 'text': code}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=CoqKernel)
