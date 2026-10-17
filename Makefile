.PHONY: install clean

install: requirements.txt
	python -m venv .venv --without-scm-ignore-files
	.venv/bin/pip install -r requirements.txt
	@echo "run source .venv/bin/activate to start venv"

clean:
	rm *.bin
	rm *.pem
