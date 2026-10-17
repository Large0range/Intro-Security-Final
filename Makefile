.PHONY: install clean

install: requirements.txt
	python -m venv .venv --without-scm-ignore-files
	.venv/bin/pip install -r requirements.txt

clean:
	rm *.bin
	rm *.pem
