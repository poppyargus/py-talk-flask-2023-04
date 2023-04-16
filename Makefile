

setup:
	virtualenv -p /usr/bin/python3 venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -r requirements_dev.txt

clean:
	rm -rf venv

lint:
	venv/bin/flake8 --exclude venv .
	venv/bin/mypy --install-types --non-interactive --exclude venv .

# could i have done w vars? yes. Worth the time when I'm on deadline? no.
pt1:
	venv/bin/flask --app pt1/app.py run

pt2:
	venv/bin/flask --app pt2/app.py run

pt3:
	venv/bin/flask --app pt3/app.py run

pt4:
	venv/bin/flask --app pt4/app.py run

pt5:
	venv/bin/flask --app pt5/app.py run

.PHONY: install clean lint pt1 pt2 pt3 pt4 pt5

