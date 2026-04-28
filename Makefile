.PHONY: install demo test clean

PYTHON ?= python
PKG := PYTHONPATH=src $(PYTHON) -m intentir.cli

install:
	$(PYTHON) -m pip install -e .

demo:
	mkdir -p build traces
	@echo "1. compiled assembly"
	$(PKG) compile-message examples/messages/repo_scan.json -o build/repo_scan.intentasm
	cat build/repo_scan.intentasm
	@echo "2. binary packet created"
	$(PKG) asm build/repo_scan.intentasm -o build/repo_scan.intentbin
	@echo "build/repo_scan.intentbin"
	@echo "3. disassembly"
	$(PKG) disasm build/repo_scan.intentbin -o build/repo_scan.disasm.intentasm
	cat build/repo_scan.disasm.intentasm
	@echo "4. verification passed"
	$(PKG) verify build/repo_scan.intentasm
	@echo "5. receiver executed CALL"
	$(PKG) recv build/repo_scan.intentbin --agent worker --execute --trace traces/repo_scan.intenttrace.jsonl
	@echo "6. trace written"
	@echo "traces/repo_scan.intenttrace.jsonl"
	@echo "7. replay succeeded"
	$(PKG) replay traces/repo_scan.intenttrace.jsonl

test:
	PYTHONPATH=src pytest tests

clean:
	rm -rf build traces/*.intenttrace.jsonl
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
