from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='coq_jupyter',
    version='1.0.0',
    packages=['coq_jupyter'],
    description='Coq kernel for Jupyter',
    long_description=readme,
    author='Eugene Loy',
    author_email='eugeny.loy@gmail.com',
    url='https://github.com/EugeneLoy/coq_jupyter',
    install_requires=[
        'jupyter_client',
        'IPython',
        'ipykernel',
        'pexpect>=4.0'
    ],
    classifiers=[
        'Intended Audience :: Developers' # TODO
    ],
)
