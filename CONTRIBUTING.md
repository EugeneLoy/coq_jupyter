Please use `development` branch to send pull requests.

---

This document assumes that you have `cd`ed into root of the repo and installed the following:

    pip install --upgrade jupyter-console setuptools wheel twine "jupyter_kernel_test>=0.3"

---

To run tests (this also installs kernel from source):

    python setup.py install
    python -m coq_jupyter.install
    python test/kernel_test.py

---

To run kernel from source (with DEBUG logging level):

    python main.py --ConnectionFileMixin.connection_file=coq_kernel.json --Application.log_level=DEBUG

... and then connect to kernel using:

    jupyter console --existing coq_kernel.json

---

To build:

    python setup.py sdist bdist_wheel

---

To publish (to TestPyPI):

    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
