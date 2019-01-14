To run kernel from source (with DEBUG logging level):

    pip install --user jupyter-console
    python main.py --ConnectionFileMixin.connection_file=coq_kernel.json --Application.log_level=DEBUG

... and then connect to kernel using:

    jupyter console --existing coq_kernel.json


To test (this also installs kernel from source):

    pip install --user --upgrade setuptools jupyter_kernel_test>=0.3
    python setup.py install --user
    python -m coq_jupyter.install
    python test/kernel_test.py


To build:

    python -m pip install --user --upgrade setuptools wheel
    python setup.py sdist bdist_wheel


To publish (to TestPyPI):

    pip install --user --upgrade twine
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
