


install:
	virtualenv -p /usr/bin/python3 venv
	venv/bin/pip install -r requirements.txt


.PHONY: install

