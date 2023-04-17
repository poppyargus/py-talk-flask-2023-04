# This is a Makefile for GNU Make.
# Make is very old, and will probably be around forever - it's worth learning!
# .PHONY means the name of the make target is not a file,
# and it should be run every time.
# `man make` to learn more about make, or search for the info page on the web.

setup:
	virtualenv -p /usr/bin/python3 venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements_dev.txt
.PHONY: setup

clean:
	rm -rf venv
.PHONY: clean

lint:
	venv/bin/flake8 --exclude venv .
	venv/bin/mypy --install-types --non-interactive --exclude venv .
.PHONY: lint

test:
	# TODO: this is janky, but everything is in one file for demo purposes
	venv/bin/pytest pt*/app.py

black:
	venv/bin/black --line-length 79 pt*
.PHONY: black

# could i have done w vars? yes. Worth the time when I'm on deadline? no.
pt1:
	venv/bin/flask --app pt1/app.py run
.PHONY: pt1

pt2:
	venv/bin/flask --app pt2/app.py run
.PHONY: pt2

pt3:
	venv/bin/flask --app pt3/app.py run
.PHONY: pt3

pt4:
	venv/bin/flask --app pt4/app.py run
.PHONY: pt4

pt5:
	venv/bin/flask --app pt5/app.py run
.PHONY: pt5

pt6:
	venv/bin/flask --app pt6/app.py run
.PHONY: pt6

pt7:
	venv/bin/flask --app pt7/app.py run
.PHONY: pt7
