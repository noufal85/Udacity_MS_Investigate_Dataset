"""Execute a clean notebook kernel and export its saved outputs to HTML."""

import json
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager


ROOT = Path(__file__).resolve().parent
(ROOT / ".cache").mkdir(exist_ok=True)
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
os.environ.setdefault("IPYTHONDIR", str(ROOT / ".cache/ipython"))
os.environ.setdefault("JUPYTER_PLATFORM_DIRS", "1")

path = ROOT / "Investigate_a_Dataset.ipynb"
nb = nbformat.read(path, as_version=4)
manager = KernelManager(kernel_name="python3")
manager.kernel_spec.argv = [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"]
client = NotebookClient(nb, km=manager, timeout=180, resources={"metadata": {"path": str(ROOT)}})
try:
    client.execute()
finally:
    if manager.has_kernel:
        manager.shutdown_kernel(now=True)
nbformat.write(nb, path)

code_cells = [cell for cell in nb.cells if cell.cell_type == "code"]
errors = [out for cell in code_cells for out in cell.outputs if out.output_type == "error"]
assert not errors
assert all(cell.execution_count is not None and cell.outputs for cell in code_cells)
exporter = HTMLExporter(template_name="lab")
body, _ = exporter.from_notebook_node(nb)
(ROOT / "Investigate_a_Dataset.html").write_text(body, encoding="utf-8")

result = {
    "cells": len(nb.cells), "executed_code_cells": len(code_cells),
    "error_outputs": len(errors),
    "embedded_png_outputs": sum("image/png" in out.get("data", {}) for cell in code_cells for out in cell.outputs),
    "html_bytes": len(body.encode("utf-8")),
}
(ROOT / "validation").mkdir(exist_ok=True)
(ROOT / "validation/execution.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
