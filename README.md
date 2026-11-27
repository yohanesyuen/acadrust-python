# acadrust-python

Native DWG ↔ DXF conversion for CPython 3.13+, powered by [acadrust](https://github.com/hakanaktt/acadrust). No CAD application, ODA converter, or Rust toolchain is needed to use a prebuilt wheel.

```python
from pathlib import Path
import acadrust

acadrust.dwg_to_dxf("input.dwg", "output.dxf")
acadrust.dxf_to_dwg("input.dxf", "output.dwg")
dxf_bytes = acadrust.dwg_to_dxf_bytes(Path("input.dwg").read_bytes())
dwg_bytes = acadrust.dxf_to_dwg_bytes(dxf_bytes)
```

`source` and `destination` accept strings and `os.PathLike` values. Byte functions accept Python `bytes`. Conversion failures raise `acadrust.ConversionError`; invalid target versions raise `ValueError`. `SUPPORTED_VERSIONS`, `ACADRUST_VERSION`, and `__version__` provide version information. `target_version="AC1027"` requests a target where upstream supports it. The native conversion runs without the Python GIL.

DXF byte output is ASCII DXF in structure, but non-ASCII text encoding follows the source document's DXF code page and acadrust's writer. It is **not guaranteed UTF-8**. For ezdxf, use its file reader after writing the bytes, or decode with the declared code page. Do not blindly call `dxf_bytes.decode("utf-8")` on arbitrary drawings.

```python
import io
import ezdxf
import acadrust

dxf = acadrust.dwg_to_dxf_bytes(open("input.dwg", "rb").read())
doc = ezdxf.read(io.StringIO(dxf.decode("utf-8").replace("\r\n", "\n")))  # Only for known UTF-8 drawings
```

Conversion is subject to upstream support for individual entities and DWG versions. Inspect results in a CAD application before using them for engineering decisions. This wrapper currently does not expose upstream read diagnostics or unsupported-object reports.

## Development

Install `uv`, Rust, Docker (for Linux wheels), and Python 3.13. Run `make dev`, `make test`, `make wheel-macos`, `make wheel-linux`, or `make wheels`. `make clean` removes generated artifacts. Linux wheels target manylinux 2.17 x86_64. `Cargo.lock` pins Rust dependencies.

## License

MPL-2.0. acadrust is MPL-2.0 and has its own third-party notices; see its repository for dependency and DWG provenance notices.
