from setuptools import setup

readme = """Jupyter kernel for Coq.
See: https://github.com/EugeneLoy/coq_jupyter
"""

setup(
    name='coq_jupyter',
    version='1.5.1',
    packages=['coq_jupyter'],
    description='Coq kernel for Jupyter',
    long_description=readme,
    author='Eugene Loy',
    author_email='eugeny.loy@gmail.com',
    url='https://github.com/EugeneLoy/coq_jupyter',
    include_package_data=True,
    install_requires=[
        'jupyter_client',
        'IPython',
        'ipykernel',
        'future',
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
