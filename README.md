# Appointment no-show investigation

Udacity's Investigate a Dataset project, using the supplied Brazilian appointment
no-show snapshot. The analysis examines age, booking lead time and recorded SMS
receipt. It describes associations and explicitly avoids causal claims.

## Report wording update

The report now uses shorter sections and plain-English explanations for readers
who do not work with statistics. Each main section explains its purpose, and
the chart discussions describe what was compared and what the results mean.
The data, cleaning rules and numerical findings are unchanged.

Setup commands, checksum verification and submission details stay in this
README and the supporting scripts. The report itself focuses on the data and
findings. The analysis used Pandas documentation for date conversion and grouped
summaries; development-tool and template-editing notes are not data references.

## Read the report

- `Investigate_a_Dataset.html`: shareable report with executed tables and embedded charts.
- `Investigate_a_Dataset.ipynb`: executed notebook; all cleaning and chart helpers are embedded.
- `figures/`: six rendered figures for visual verification.
- `PROJECT_REQUIREMENTS.md`: source register, analysis decisions and rubric matrix.
- `validation/`: execution checks and reproducibility evidence.

The notebook and HTML are the core course deliverables. The raw CSV, source
archive, virtual environment, caches and checkpoint files are excluded from
the submission/public-repository file set. No API key is needed.

## Reproduce

Use Python 3.13 and create an isolated environment:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Retrieve the exact CSV from the original course archive, or from the course's
download URL. Both paths verify its SHA-256 against the analyzed snapshot:

```bash
python prepare_data.py --archive ../1793344540.tar.gz
# Alternatively, for a fresh checkout without the archive:
python prepare_data.py --download
```

The course URL returned HTTP 403 during publication checks. `--download` tries
that URL first, then an immutable public GitHub mirror containing the exact
same CSV bytes. Its checksum must match the analyzed course snapshot before
anything is saved. The raw CSV is still excluded from this repository.

Run the tests and execute the notebook from a clean kernel:

```bash
python -m unittest discover -s tests -v
python execute_report.py
```

`execute_report.py` uses the current Python executable for the kernel, updates
the saved notebook, exports the HTML, and checks that every code cell executed
with nonempty outputs and without an error output. It needs permission to open
local Jupyter kernel sockets. You can also use Jupyter's Restart and Run All,
save the notebook, and export it with `jupyter nbconvert --to html`.

`build_notebook.py` regenerates the unexecuted notebook source from the supplied
CSV and tested helpers. Run it only when intentionally rebuilding the source,
then execute the notebook again before submission:

```bash
python build_notebook.py
python execute_report.py
```

The generated narrative numbers depend on the checksum-verified snapshot.
Changing the dataset or analysis logic requires rebuilding and reexecuting the
report; do not reuse the existing conclusions for different data.

## Analysis boundaries

The unit is the appointment. Repeated patients are retained and acknowledged.
`No-show = Yes` encodes a missed appointment. Lead time compares normalized
calendar dates, since appointment times are unavailable. One negative age and
five negative lead times are excluded; missing values are not imputed. The
study is exploratory and contains no predictive model or inferential test.

Public repository: [noufal85/Udacity_MS_Investigate_Dataset](https://github.com/noufal85/Udacity_MS_Investigate_Dataset).
The published notebook and HTML contain saved execution results. Raw input is
retrieved separately using the commands above. GitHub publication does not
submit the project through the Udacity course platform.
