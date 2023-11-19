test:
	coverage erase
	coverage run --branch --omit tests.py -m unittest -v tests.py
	coverage report -m kwbar.py
	coverage xml

clean:
	rm -f coverage.xml
	rm -rf dist/
	rm -rf .ruff_cache/

build:
	poetry build