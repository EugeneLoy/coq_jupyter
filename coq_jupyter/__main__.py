from ipykernel.kernelapp import IPKernelApp
from .kernel import CoqKernel

IPKernelApp.launch_instance(kernel_class=CoqKernel)
