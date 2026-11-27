use std::io::Cursor;

use acadrust::{DwgReader, DwgWriter, DxfReader, DxfVersion, DxfWriter};
use pyo3::exceptions::{PyException, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyModule};

pyo3::create_exception!(_acadrust, ConversionError, PyException);

fn version(value: Option<&str>) -> PyResult<Option<DxfVersion>> {
    value
        .map(|v| {
            DxfVersion::parse(v)
                .ok_or_else(|| PyValueError::new_err(format!("unsupported CAD version: {v}")))
        })
        .transpose()
}

fn convert(input: &[u8], to_dxf: bool, target: Option<DxfVersion>) -> PyResult<Vec<u8>> {
    let result = std::panic::catch_unwind(|| -> Result<Vec<u8>, String> {
        if to_dxf {
            let doc = DwgReader::from_stream(Cursor::new(input.to_vec()))
                .read()
                .map_err(|e| e.to_string())?;
            let writer = match target {
                Some(v) => DxfWriter::new(&doc).with_version(v),
                None => DxfWriter::new(&doc),
            };
            writer.write_to_vec().map_err(|e| e.to_string())
        } else {
            let mut doc = DxfReader::from_reader(Cursor::new(input.to_vec()))
                .map_err(|e| e.to_string())?
                .read()
                .map_err(|e| e.to_string())?;
            if let Some(v) = target {
                doc.version = v;
            }
            DwgWriter::write_to_vec(&doc).map_err(|e| e.to_string())
        }
    });
    match result {
        Ok(Ok(bytes)) => Ok(bytes),
        Ok(Err(message)) => Err(ConversionError::new_err(message)),
        Err(_) => Err(ConversionError::new_err(
            "acadrust panicked while converting the drawing",
        )),
    }
}

#[pyfunction]
#[pyo3(signature = (data, target_version=None))]
fn dwg_to_dxf_bytes<'py>(
    py: Python<'py>,
    data: &[u8],
    target_version: Option<&str>,
) -> PyResult<Bound<'py, PyBytes>> {
    let target = version(target_version)?;
    let bytes = py.allow_threads(|| convert(data, true, target))?;
    Ok(PyBytes::new(py, &bytes))
}

#[pyfunction]
#[pyo3(signature = (data, target_version=None))]
fn dxf_to_dwg_bytes<'py>(
    py: Python<'py>,
    data: &[u8],
    target_version: Option<&str>,
) -> PyResult<Bound<'py, PyBytes>> {
    let target = version(target_version)?;
    let bytes = py.allow_threads(|| convert(data, false, target))?;
    Ok(PyBytes::new(py, &bytes))
}

#[pymodule]
fn _acadrust(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add("ConversionError", module.py().get_type::<ConversionError>())?;
    module.add_function(wrap_pyfunction!(dwg_to_dxf_bytes, module)?)?;
    module.add_function(wrap_pyfunction!(dxf_to_dwg_bytes, module)?)?;
    module.add(
        "SUPPORTED_VERSIONS",
        [
            "AC1009", "AC1012", "AC1014", "AC1015", "AC1018", "AC1021", "AC1024", "AC1027",
            "AC1032",
        ],
    )?;
    module.add("ACADRUST_VERSION", "0.6.8")?;
    Ok(())
}
