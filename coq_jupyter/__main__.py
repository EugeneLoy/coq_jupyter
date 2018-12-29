from ipykernel.kernelapp import IPKernelApp
from sys import argv
from .kernel import CoqKernel

IPKernelApp.launch_instance(kernel_class=CoqKernel, args=argv)
