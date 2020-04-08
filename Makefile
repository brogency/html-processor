SHELL := /bin/bash

test:
	poetry run coverage run --source=html_processor -m pytest && \
	poetry run coverage report --fail-under=97 -m && exit
