UV ?= uv

.PHONY: dev test wheel-macos wheel-linux wheels clean
dev:
	$(UV) tool run --from maturin==1.10.2 maturin develop --uv --release
test:
	$(UV) pip install --python .venv/bin/python pytest==8.4.2 ezdxf==1.4.2
	.venv/bin/python -m pytest -q
wheel-macos:
	$(UV) tool run --from maturin==1.10.2 maturin build --release --locked --out dist
wheel-linux:
	docker run --rm --platform linux/amd64 -v "$(CURDIR):/io" ghcr.io/pyo3/maturin:v1.10.2 build --release --locked --compatibility manylinux_2_17 --out /io/dist
wheels: wheel-macos wheel-linux
clean:
	rm -rf target dist .venv .pytest_cache
