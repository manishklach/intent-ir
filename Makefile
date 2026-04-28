.PHONY: install demo test clean

install:
	pip install -e .

demo:
	mkdir -p build
	python -m intentir.cli compile examples/hello_agent/task.json -o build/hello.ir
	python -m intentir.cli asm build/hello.ir -o build/hello.bin
	python -m intentir.cli disasm build/hello.bin
	python -m intentir.cli run build/hello.ir --trace traces/hello_agent.trace.jsonl
	python -m intentir.cli replay traces/hello_agent.trace.jsonl

test:
	pytest tests/

clean:
	rm -rf build/
	rm -f *.ir *.bin
	find . -type d -name "__pycache__" -exec rm -rf {} +
