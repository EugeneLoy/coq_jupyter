import argparse
import json
import os
import sys
import shutil

from jupyter_client.kernelspec import KernelSpecManager
from IPython.utils.tempdir import TemporaryDirectory

def kernel_json(display_name, coqtop_executable, coqtop_args):
    argv = [sys.executable, "-m", "coq_jupyter", "-f", "{connection_file}"]
    if coqtop_executable is not None:
        argv.append('--CoqKernel.coqtop_executable="{}"'.format(coqtop_executable))
    if coqtop_args is not None:
        argv.append('--CoqKernel.coqtop_args="{}"'.format(coqtop_args))

    return {
        "argv": argv,
        "display_name": display_name,
        "language": "coq",
    }

def install_kernel_spec(user, prefix, kernel_name, kernel_display_name, coqtop_executable, coqtop_args):
    with TemporaryDirectory() as td:
        os.chmod(td, 0o755) # Starts off as 700, not user readable

        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(kernel_json(kernel_display_name, coqtop_executable, coqtop_args), f, sort_keys=True)

        shutil.copyfile(
            os.path.join(os.path.dirname(__file__), "kernel.js"),
            os.path.join(td, 'kernel.js')
        )

        print('Installing Jupyter kernel spec')
        KernelSpecManager().install_kernel_spec(td, kernel_name, user=user, replace=True, prefix=prefix)

def _is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False # assume not an admin on non-Unix platforms

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--user', action='store_true', help="Install to the per-user kernels registry. Default if not root.")
    ap.add_argument('--sys-prefix', action='store_true', help="Install to sys.prefix (e.g. a virtualenv or conda env)")
    ap.add_argument('--prefix', help="Install to the given prefix. Kernelspec will be installed in {PREFIX}/share/jupyter/kernels/")
    ap.add_argument('--kernel-name', help="Kernelspec name. Default is 'coq'.")
    ap.add_argument('--kernel-display-name', help="Kernelspec name that will be used in UI. Default is 'Coq'.")
    ap.add_argument('--coqtop-executable', help="coqidetop executable (coqtop for coq versions before 8.9.0).")
    ap.add_argument('--coqtop-args', help="Arguments to add when launching coqtop.")

    args = ap.parse_args(argv)

    if args.sys_prefix:
        args.prefix = sys.prefix
    if not args.prefix and not _is_root():
        args.user = True
    if not args.kernel_name:
        args.kernel_name = 'coq'
    if not args.kernel_display_name:
        args.kernel_display_name = 'Coq'

    install_kernel_spec(
        args.user,
        args.prefix,
        args.kernel_name,
        args.kernel_display_name,
        args.coqtop_executable,
        args.coqtop_args
    )

if __name__ == '__main__':
    main()
