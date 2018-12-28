
To build:

    python -m pip install --user --upgrade setuptools wheel
    python setup.py sdist bdist_wheel

To publish (to TestPyPI):

    pip install --user --upgrade twine
    python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
