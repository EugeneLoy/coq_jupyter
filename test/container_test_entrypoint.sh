#!/bin/bash

export OPAMROOT=/home/coq/.opam
eval $(opam env)

sudo apt-get update
sudo apt-get install -y python3-pip

python3 --version
coqtop --version

sudo pip3 install --upgrade --force-reinstall /github/workspace/dist/coq_jupyter-*.tar.gz 'jupyter_client<=6.1.12' 'jupyter_kernel_test<=0.3'
sudo python3 -m coq_jupyter.install

python3 /github/workspace/test/kernel_test.py -v
