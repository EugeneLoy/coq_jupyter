
# This entry point is used for debug only:
if __name__ == '__main__':
    from sys import argv
    from ipykernel.kernelapp import IPKernelApp
    from coq_jupyter.kernel import CoqKernel
    IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
