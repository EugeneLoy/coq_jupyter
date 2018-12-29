To run kernel from source with INFO logging:

    python -m pip install --user jupyter-console
    python coq_jupyter/kernel.py --ConnectionFileMixin.connection_file=coq_kernel.json --Application.log_level=INFO

... and then connect to kernel using:

    jupyter console --existing coq_kernel.json


To build:

    python -m pip install --user --upgrade setuptools wheel
    python setup.py sdist bdist_wheel


To publish (to TestPyPI):

    pip install --user --upgrade twine
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
