install:
	pip install coq-jupyter
	python -m coq_jupyter.install

install-local:
	pip install .
	python -m coq_jupyter.install

uninstall:
	jupyter kernelspec uninstall coq
	pip uninstall coq_jupyter
