venv:
	python3 -m venv venv

develop: venv
	venv/bin/pip install -e ".[dev]"

dist: clean venv
	venv/bin/python3 -m pip install --upgrade setuptools wheel
	venv/bin/python3 setup.py sdist bdist_wheel

publish: venv
	venv/bin/python3 -m pip install twine
	venv/bin/twine upload dist/*

clean:
	rm -r dist || true
	rm -r venv || true
