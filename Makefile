

install:
	virtualenv -p /usr/bin/python3 venv
	venv/bin/pip install -r requirements.txt

clean:
	rm -rf venv


.PHONY: install

