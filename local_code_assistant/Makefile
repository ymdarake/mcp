# Makefile for the packaged local_assistant

.PHONY: help test smoke run clean

help:
	@echo "Targets: test, smoke, run, clean"

test:
	@echo "Running tests..."
	python3 -m unittest discover -s tests -p 'test_*.py' -v

smoke:
	@echo "Smoke test: list_files against current directory"
	echo '{"command":"list_files","params":{"directory":"."}}' | python3 local_code_assistant.py --project $(CURDIR)

run:
	@echo "Start assistant (stdin JSON)"
	python3 local_code_assistant.py --project $(CURDIR)

clean:
	-find . -type f -name '*.pyc' -delete || true
	-find . -type d -name '__pycache__' -exec rm -rf {} + || true
