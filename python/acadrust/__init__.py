"""Native DWG/DXF conversion using acadrust."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TypeAlias

from ._acadrust import (
    ACADRUST_VERSION,
    SUPPORTED_VERSIONS,
    ConversionError,
    dwg_to_dxf_bytes,
    dxf_to_dwg_bytes,
)

__version__ = "0.1.0"
PathLike: TypeAlias = str | os.PathLike[str]


def dwg_to_dxf(source: PathLike, destination: PathLike, *, target_version: str | None = None) -> None:
    """Convert a DWG file to an ASCII DXF file."""
    Path(destination).write_bytes(dwg_to_dxf_bytes(Path(source).read_bytes(), target_version))


def dxf_to_dwg(source: PathLike, destination: PathLike, *, target_version: str | None = None) -> None:
    """Convert a DXF file to a DWG file."""
    Path(destination).write_bytes(dxf_to_dwg_bytes(Path(source).read_bytes(), target_version))


__all__ = ["ACADRUST_VERSION", "SUPPORTED_VERSIONS", "ConversionError", "__version__", "dwg_to_dxf", "dxf_to_dwg", "dwg_to_dxf_bytes", "dxf_to_dwg_bytes"]
