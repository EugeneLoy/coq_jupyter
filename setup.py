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
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
        'Framework :: Jupyter',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development'
    ],
)
