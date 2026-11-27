import io

import ezdxf
import pytest

import acadrust


def sample():
    doc = ezdxf.new("R2013")
    space = doc.modelspace()
    space.add_line((1, 2), (3, 4))
    space.add_circle((5, 6), 2)
    space.add_arc((0, 0), 3, 10, 80)
    space.add_lwpolyline([(0, 0), (1, 2), (3, 2)])
    space.add_text("Hello")
    space.add_mtext("Unicode: café")
    doc.layers.new("TEST_LAYER")
    block = doc.blocks.new("TEST_BLOCK")
    block.add_line((0, 0), (2, 0))
    insert = space.add_blockref("TEST_BLOCK", (10, 20), dxfattribs={"layer": "TEST_LAYER"})
    insert.add_attrib("ID", "A1")
    stream = io.StringIO()
    doc.write(stream)
    return stream.getvalue().encode("utf-8")


def test_round_trip_bytes():
    dwg = acadrust.dxf_to_dwg_bytes(sample())
    assert dwg.startswith(b"AC")
    result = acadrust.dwg_to_dxf_bytes(dwg)
    drawing = ezdxf.read(io.StringIO(result.decode("utf-8").replace("\r\n", "\n")))
    counts = [e.dxftype() for e in drawing.modelspace()]
    for kind in ("LINE", "CIRCLE", "ARC", "LWPOLYLINE", "TEXT", "MTEXT", "INSERT"):
        assert kind in counts
    assert "TEST_LAYER" in drawing.layers
    assert "TEST_BLOCK" in drawing.blocks
    assert drawing.modelspace().query("INSERT")[0].get_attrib("ID").dxf.text == "A1"


def test_files(tmp_path):
    source = tmp_path / "input.dxf"
    dwg = tmp_path / "output.dwg"
    dxf = tmp_path / "output.dxf"
    source.write_bytes(sample())
    acadrust.dxf_to_dwg(source, dwg)
    acadrust.dwg_to_dxf(dwg, dxf)
    assert dxf.read_bytes()


def test_invalid():
    with pytest.raises(acadrust.ConversionError):
        acadrust.dwg_to_dxf_bytes(b"invalid")
    with pytest.raises(ValueError):
        acadrust.dxf_to_dwg_bytes(sample(), "bad-version")


@pytest.mark.parametrize("version", ["AC1015", "AC1027", "AC1032"])
def test_target_versions(version):
    dwg = acadrust.dxf_to_dwg_bytes(sample(), version)
    assert dwg.startswith(version.encode())
    dxf = acadrust.dwg_to_dxf_bytes(dwg, version)
    encoding = "cp1252" if version == "AC1015" else "utf-8"
    drawing = ezdxf.read(io.StringIO(dxf.decode(encoding).replace("\r\n", "\n")))
    assert drawing.dxfversion == version


def test_truncated():
    dwg = acadrust.dxf_to_dwg_bytes(sample())
    with pytest.raises(acadrust.ConversionError):
        acadrust.dwg_to_dxf_bytes(dwg[:16])
