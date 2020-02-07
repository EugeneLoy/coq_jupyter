[![PyPI version](https://badge.fury.io/py/coq-jupyter.svg)](https://badge.fury.io/py/coq-jupyter) [![Conda version](https://img.shields.io/conda/vn/conda-forge/coq-jupyter.svg?label="conda%20package")](https://github.com/conda-forge/coq-jupyter-feedstock) [![Build Status](https://travis-ci.com/EugeneLoy/coq_jupyter.svg?branch=master)](https://travis-ci.com/EugeneLoy/coq_jupyter) [![Join the chat at https://gitter.im/coq_jupyter/community](https://badges.gitter.im/coq_jupyter/community.svg)](https://gitter.im/coq_jupyter/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![badge](https://img.shields.io/badge/launch%20demo-binder-579ACA.svg?logo=data:image/png;base64,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)](https://mybinder.org/v2/gh/EugeneLoy/coq_jupyter_demo/master?filepath=demo.ipynb)

A [Jupyter](https://jupyter.org/) kernel for [Coq](https://coq.inria.fr/).

You can try it [online in Binder](https://mybinder.org/v2/gh/EugeneLoy/coq_jupyter_demo/master?filepath=demo.ipynb).

## Installation

Make sure that CoqIDE (8.6 or newer) is installed and `coqidetop` (or `coqtop` for coq versions before 8.9.0) is in your `PATH`.

After that install using `pip` (works with python 2/3):

    pip install coq-jupyter
    python -m coq_jupyter.install

Alternatively, use Conda to install both `coqidetop` and `coq_jupyter`. For this,
install Conda (either Anaconda, Miniconda, Minimamba) and do:
```
$ conda config --add channels conda-forge
$ conda create -n coq coq-jupyter
$ conda activate coq
```


## Backtracking

There are number of convenience improvements over standard Jupyter notebook behaviour that are implemented to support Coq-specific use cases.

By default, running cell will rollback any code that was executed in that cell before. If needed, this can be disabled on a per-cell basis (using `Auto rollback` checkbox).

Manual cell rollback is also available using `Rollback cell` button (at the bottom of executed cell) or shortcut (`Ctrl+Backspace`).

## Configuring kernel

You can configure kernel by passing additional arguments during kernel installation:

* `--kernel-name` - name of the kernel

* `--kernel-display-name` - name of the kernel that will be displayed in Jupyter UI

* `--coqtop-executable` - specifies `coqidetop`/`coqtop` executable

* `--coqtop-args` - additional arguments to supply to `coqidetop`/`coqtop`

For example, to add kernel that instructs `coqidetop` to load `/workspace/init.v` on startup:

    python -m coq_jupyter.install --kernel-name=coq_with_init --kernel-display-name="Coq (with init.v)" --coqtop-executable="/usr/bin/coqidetop" --coqtop-args="-l /workspace/init.v"

## Contributing

Give feedback with [issues](https://github.com/EugeneLoy/coq_jupyter/issues) or [gitter](https://gitter.im/coq_jupyter/community), send pull requests. Also check out [CONTRIBUTING.md](CONTRIBUTING.md) for instructions.
