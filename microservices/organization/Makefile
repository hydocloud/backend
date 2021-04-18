.PHONY: target dev format lint test coverage-html pr  build build-docs build-docs-api build-docs-website
.PHONY: docs-local docs-api-local security-baseline complexity-baseline release-prod release-test release

test:
	pytest tests/ --cov=./create_organization --cov=./delete_organization --cov=./edit_organization --cov=./get_organizations