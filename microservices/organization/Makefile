format:
	isort -rc .
	black src
	black tests

test:
	export POWERTOOLS_TRACE_DISABLED=True
	coverage run -m pytest tests --disable-warnings && coverage report -m