format:
	isort -rc .
	black src
	black tests

test:
	coverage run -m pytest tests --disable-warnings && coverage report -m