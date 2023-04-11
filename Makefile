

install:
	virtualenv -p /usr/bin/python3 venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements_dev.txt

clean:
	rm -rf venv

lint:
	venv/bin/flake8 --exclude venv .
	venv/bin/mypy --exclude venv .


.PHONY: install clean lint

