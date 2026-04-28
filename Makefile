.PHONY: install demo demo-safety test clean

PYTHON ?= python3
PKG := PYTHONPATH=src $(PYTHON) -m intentir.cli
PRINT_FILE = $(PYTHON) -c "from pathlib import Path; print(Path(r'$(1)').read_text(encoding='utf-8'), end='')"
PRINT_REJECTIONS = $(PYTHON) -c "import json; from pathlib import Path; [print('[reject-trace]', entry.get('message')) for entry in (json.loads(line) for line in Path(r'$(1)').read_text(encoding='utf-8').splitlines() if line.strip()) if entry.get('outcome') == 'reject']"
ENSURE_DIRS = $(PYTHON) -c "from pathlib import Path; [Path(x).mkdir(parents=True, exist_ok=True) for x in ('build','traces')]"

install:
	$(PYTHON) -m pip install -e .

demo:
	$(ENSURE_DIRS)
	@echo "1. compiled assembly"
	$(PKG) compile-message examples/messages/repo_scan.json -o build/repo_scan.intentasm
	$(call PRINT_FILE,build/repo_scan.intentasm)
	@echo "2. binary packet created"
	$(PKG) asm build/repo_scan.intentasm -o build/repo_scan.intentbin
	@echo "build/repo_scan.intentbin"
	@echo "3. disassembly"
	$(PKG) disasm build/repo_scan.intentbin -o build/repo_scan.disasm.intentasm
	$(call PRINT_FILE,build/repo_scan.disasm.intentasm)
	@echo "4. verification passed"
	$(PKG) verify build/repo_scan.intentasm
	@echo "5. receiver executed CALL"
	$(PKG) recv build/repo_scan.intentbin --agent worker --execute --trace traces/repo_scan.intenttrace.jsonl
	@echo "6. trace written"
	@echo "traces/repo_scan.intenttrace.jsonl"
	@echo "7. replay succeeded"
	$(PKG) replay traces/repo_scan.intenttrace.jsonl

demo-safety:
	$(ENSURE_DIRS)
	@echo "1. compile safe message"
	$(PKG) compile-message examples/messages/safe_repo_scan.json -o build/safe_repo_scan.intentasm
	@echo "2. assemble safe packet"
	$(PKG) asm build/safe_repo_scan.intentasm -o build/safe_repo_scan.intentbin
	@echo "3. recv/execute safe packet"
	$(PKG) recv build/safe_repo_scan.intentbin --agent worker --policy policies/worker.policy.json --execute --trace traces/safe_repo_scan.intenttrace.jsonl
	@echo "SAFE: allowed by policy"
	@echo "SAFE: executed"
	@echo "4. replay safe trace"
	$(PKG) replay traces/safe_repo_scan.intenttrace.jsonl
	@echo "5. compile unsafe shell message"
	$(PKG) compile-message examples/messages/unsafe_shell.json -o build/unsafe_shell.intentasm
	@echo "6. assemble unsafe shell packet"
	$(PKG) asm build/unsafe_shell.intentasm -o build/unsafe_shell.intentbin
	@echo "7. recv unsafe shell packet"
	$(PKG) recv build/unsafe_shell.intentbin --agent worker --policy policies/worker.policy.json --execute --trace traces/unsafe_shell.intenttrace.jsonl
	@echo "UNSAFE SHELL: rejected by policy"
	@echo "8. show shell verifier rejection"
	$(call PRINT_REJECTIONS,traces/unsafe_shell.intenttrace.jsonl)
	@echo "9. replay unsafe shell trace"
	$(PKG) replay traces/unsafe_shell.intenttrace.jsonl
	@echo "10. compile unsafe budget message"
	$(PKG) compile-message examples/messages/unsafe_budget.json -o build/unsafe_budget.intentasm
	@echo "11. assemble unsafe budget packet"
	$(PKG) asm build/unsafe_budget.intentasm -o build/unsafe_budget.intentbin
	@echo "12. recv unsafe budget packet"
	$(PKG) recv build/unsafe_budget.intentbin --agent worker --policy policies/worker.policy.json --execute --trace traces/unsafe_budget.intenttrace.jsonl
	@echo "UNSAFE BUDGET: rejected by policy"
	@echo "13. replay unsafe budget trace"
	$(PKG) replay traces/unsafe_budget.intenttrace.jsonl

test:
	PYTHONPATH=src $(PYTHON) -m pytest tests

clean:
	$(PYTHON) -c "from pathlib import Path; import shutil; shutil.rmtree('build', ignore_errors=True); [p.unlink() for p in Path('traces').glob('*.intenttrace.jsonl') if p.is_file()]"
