# Investigation plan and rubric matrix

## Source register and authority

| Source | Authority and intake status | Requirements used |
|---|---|---|
| `../Course Overview.docx` | Assignment and rubric; all text/tables read, all 11 rendered pages inspected | Choose one supplied dataset; perform and communicate exploratory analysis; submit notebook plus HTML/PDF |
| `../1793344540.tar.gz` | Supplied assets; 11 members checked, no traversal paths or links; notebook cells inspected | Preserve `Investigate_a_Dataset.ipynb`; use supplied no-show CSV |
| Starter notebook inside the archive | Structural guidance; all 13 cells read | Introduction, questions, wrangling, exploratory analysis, conclusions and limitations |
| Pandas official documentation via Context7 | API reference | Datetime normalization, vectorized transformations and named aggregation |

The assignment/rubric controls analysis requirements. The Udacity project skill
adds public-repository preparation. The course describes workspace submission or
a ZIP upload; the skill calls for a public GitHub handoff without archives.
Prepare the notebook, HTML and a clean local repository-ready folder first.
The owner subsequently authorized public GitHub publication and two independent
reviews. Repository: `noufal85/Udacity_MS_Investigate_Dataset`. Course-platform
submission is a separate action and is not claimed here.

## Chosen investigation

Dataset: 110,527 Brazilian appointment records in the supplied no-show CSV.
Unit: appointment, not unique patient. Outcome: whether the patient did not attend.
Question: How are appointment no-show rates associated with age, calendar-day
booking lead time, and recorded SMS receipt?

Investigate each predictor's distribution and its relationship with the outcome;
also compare SMS groups within lead-time and age bands to expose group-composition
differences. Treat SMS receipt as an observed flag with unknown timing and
selection; do not interpret its association as an SMS intervention effect.

Use explicit rules for invalid ages, invalid/missing dates, negative lead times,
missing critical fields, and duplicate appointment records. Normalize timestamps
before calculating calendar-day lead time. Preserve repeated patient appointments,
report them, and explain why observations are not necessarily independent.
Keep small denominators visible. Use descriptive statistics only; no predictive
model, hypothesis test, confidence interval, or causal conclusion is required.

## Rubric and verification matrix

| ID | Requirement | Artifact and verification | Status |
|---|---|---|---|
| R1 | Functional reproducible code | Clean kernel executed all 10 code cells; no error outputs; 10 focused tests | Verified |
| R2 | Appropriate NumPy/Pandas and vectorization | Pandas parsing, categorical bands, vectorized outcome/lead-time derivation, NumPy plot bins/index arrays | Verified |
| R3 | At least one helper function used more than once | `group_rates` and `label_plot` reused across analyses; tested helpers embedded in notebook | Verified |
| R4 | Clearly posed questions answered by the analysis | Four questions; each followed by computed tables, figures and findings | Verified |
| R5 | Cleaning decisions documented and justified | Sequential audit accounts for 1 negative age and 5 negative lead times; raw missingness/duplicates checked | Verified |
| R6 | Three predictors; univariate and bivariate exploration | Age, lead time, SMS distributions and outcome comparisons; stratified synthesis | Verified |
| R7 | At least two plot types and relevant statistics | Histograms, count/rate bars and heatmap; all 6 figures visually inspected | Verified |
| R8 | Accurate tentative conclusions and limitations | Findings rechecked against actual rates; repeated patients, confounding, timing, scope and missing context discussed | Verified |
| R9 | Logical notebook flow with Markdown explanations | All required sections, meaningful comments in all 10 code cells, no remaining template tips/placeholders | Verified |
| R10 | Appropriate plot types, labels, scales and legends | All figure PNGs inspected; HTML structure contains tables, headings and six embedded PNGs | Verified |
| R11 | Executed notebook and shareable report | 28 cells, 10 executed code cells with nonempty outputs, 0 error outputs; HTML export verified | Verified |
| R12 | Submission hygiene | Explicit file list and ignore rules exclude raw CSV, archive, environment and caches; no identifiers shown in previews | Verified; publication authorized |

## Work sequence

1. Profile the supplied CSV without altering it and record its checksum.
2. Write focused cleaning/rate-table tests and verify expected failures.
3. Implement minimal reusable transformations and plotting helpers.
4. Author the notebook with computed findings and descriptive limitations.
5. Execute all cells, inspect outputs and charts, export HTML.
6. Compare a small set of public repository structures without copying their work.
7. Reconcile every rubric row, inspect deliverables and report publication readiness.

## Validation outcomes

The raw CSV SHA-256 is
`9132d3e7d0246617df9041d3764f20ad6f08e7b0d9f0997fa254fc5e52eda27d`.
There are 110,527 raw appointments, 110,521 retained appointments and 22,314
retained no-shows (20.189828%). The retained appointments represent 62,298
distinct patient identifiers. Source data remains locally available for execution
but is excluded from the intended submission file list.

The recorded SMS cohorts have different crude no-show rates: 16.698% without an
SMS recorded and 27.575% with one. The direction reverses in all five lead-time
bands where both cohorts appear. This is verified descriptively and does not
establish a reminder effect. The absence of same-day SMS observations remains
missing, rather than being converted to a zero rate.

The notebook executed in a clean Jupyter kernel using the project environment.
The sandbox initially prevented Jupyter's local sockets; execution succeeded
with the approved local-kernel permission. Dependency installation also used
approved network access. Neither environment limitation was treated as a data
or functional validation failure.

## Comparative public repository review

Public file trees were inspected through GitHub's API. They are observational
references for artifact organization, not sources of code, conclusions or
evidence of grading success.

| Reference | Observation used for review |
|---|---|
| `https://github.com/shahadasseri/No-show-appointments-Data-Analysis` | Contains a notebook, matching HTML and README, supporting a visible shareable-report handoff |
| `https://github.com/roominy/project2_udacity_no_show_appointments_dataset_Investigation` | Contains both notebook and HTML; checked that our export is present rather than relying only on notebook source |
| `https://github.com/hada-megha13/udacity-NoShowAppointments` | Listed tree contains a notebook and README, but no HTML; the supplied rubric still requires this project's shareable export |

Some reference trees include their raw CSV. That practice is not adopted here:
this assignment says the dataset need not be submitted, and data retrieval is
documented separately. No external notebook, analysis prose or figure was copied.

## Independent publication reviews

Two independent agents checked the supplied rubric, analysis, saved execution
outputs and reproducibility. Both recomputed the cohort totals and SMS reversal
and found no statistical or rubric blocker. The tests now explicitly select a
headless Matplotlib backend after the reviewers reproduced a native-backend
crash on macOS. A metadata entry was corrected to list only the two helpers
actually reused within the notebook.

A fresh-checkout download check found that the course-hosted CSV returned HTTP
403. The public CSV mirror in `shahadasseri/No-show-appointments-Data-Analysis`
matches the course snapshot's SHA-256 exactly. `prepare_data.py` now tries the
course first, then the mirror pinned to commit
`9a015604477dbaaadd4187b9b80522abdb722bb3`, and verifies the checksum before saving.
This downloads source data only; it does not copy another student's analysis
or publish raw data. A regression test covers the HTTP-403 fallback path.

## Writing feedback received November 3, 2026

The user supplied writing feedback and a screenshot of the published report.
The local revision is `3b564a4`; no separate evaluator commit was provided.
This revision addresses clarity and organization while preserving the source
data, cleaning rules, calculations and conclusions. Comments about possible
AI authorship are not treated as evidence of authorship or as a request to
misrepresent how the work was produced.

| Feedback | Change and verification | Status |
|---|---|---|
| Use easy-to-understand English | Rewrote explanations for a reader without a statistics background; two independent reviewers confirmed clarity and unchanged findings | Verified |
| Break up dense report sections | Used shorter Markdown cells and focused subsections, especially findings and limitations | Verified |
| Keep the template's clear sections | Retained introduction, questions, data wrangling, exploration, conclusions and limitations | Verified |
| Explain each section's purpose | Started each main section and analysis question with a short introduction | Verified |
| Explain the charts and findings | Described comparisons, results and limits; reviewed the saved notebook, HTML content and chart images | Verified |
| Keep process notes out of the analysis | Kept setup, packaging and integrity details in README/code; removed tool and template-editing commentary from report prose | Verified |
| Prevent recurrence in the project skill | Added a plain-language report check to the local udacity-project skill, retaining accuracy and required AI disclosures; skill validator passed | Verified |

Both independent follow-up reviewers approved the writing revision without
blockers. The canonical analysis code is unchanged from `3b564a4`; the rebuilt
notebook executed all 10 code cells with no errors and six embedded figures.
All eight tests passed. HTML content was checked locally; a browser layout
inspection was unavailable because the browser rejected the local file URL.

## Focused wording follow-up

The no-ai-slop review inspected revision `cd1f38b` on `main`. The owner
authorized the three suggested trims and publication. This is a writing-only
change; required sections, numbers, methods and limitations must stay intact.

| Finding | Planned change | Verification | Status |
|---|---|---|---|
| Generic conclusion opening | Began with the appointment totals | Rebuilt notebook and HTML contain the direct opening | Verified |
| Repeated age-and-delay commentary | Kept the numerical example and explanation of group sizes | Only Markdown cells 24 and 25 changed; code sources and chart images are identical | Verified |
| Repeated conclusion recap | Kept the caution about causation without another summary | Saved exports reviewed against the writing skill's evaluation guide | Verified |

The no-ai-slop evaluation checks passed for this focused edit. Required
headings, useful section introductions, specific numerical findings and
methodological cautions remain. No claims about authorship are made.
The notebook executed all 10 code cells without errors and retained six
charts; all eight tests passed. An independent reviewer approved the exact
revised notebook and HTML and independently reran all eight tests.
Validation file hashes are refreshed before publication; the final handoff
reports the verified remote revision.

## Code-comment feedback

The user supplied feedback requiring comments within code cells and reasoning
for cleaning, summaries and plots. The local baseline is `184a563` on `main`;
the reviewer did not identify a separate evaluated commit. Existing template
sections and Markdown explanations are retained. The supplied Simplilearn
comments article could not be retrieved during intake; the complete pasted
feedback is the requirement used here.

| Feedback | Planned change | Verification | Status |
|---|---|---|---|
| Comments within code cells | Added concise reasons for the choices in each code cell, including embedded helpers | Saved-notebook comment regression test and two independent reviews | Verified |
| Explain cleaning and analysis decisions | Commented on ID types, date handling, invalid values, group sizes, rates and empty groups | Analysis AST matches baseline; comments are visible in the HTML | Verified |
| Explain descriptive summaries and spread | Retained describe(); added standard deviation to the cleaned age/delay summary and explained it | Saved-output regression test and independently recomputed statistics | Verified |
| Explain plot choices and interpretations | Commented on histogram bins, rate comparisons, shared booking delays and heatmap counts | All six chart images match baseline exactly; Markdown interpretations retained | Verified |
| Preserve notebook flow and limits | Kept all six requested sections and the descriptive, noncausal scope | Heading, numerical-result and no-ai-slop evaluation checks passed | Verified |

Both new tests failed on the original saved notebook before editing and passed
after regeneration. All 10 tests pass. The notebook executed all 10 code cells
without errors and retained six figures. Both independent reviewers approved
the saved notebook and HTML without blockers. The cleaned booking-delay median,
mean and standard deviation are 4, 10.184345 and 15.255153 days, respectively.
The report rounds them to 4, 10.2 and 15.3 days.

Only the cleaned-data summary changes executable notebook behavior, by adding
standard deviation. The analysis module's syntax tree is unchanged; the other
nine code-cell outputs and all six chart images match `184a563` exactly.
The no-ai-slop evaluation retains necessary comments, rubric headings, methods
and limitations. Static HTML content was checked; no browser layout review is
claimed. This update is prepared locally; no new commit, push or Udacity
submission is assumed from the feedback alone.

## Final writing review

The user requested a further check against the earlier writing feedback.
Scope: the current local notebook, saved HTML, README and code comments.
The existing code-comment revision is preserved; this is not an AI-authorship
test or an attempt to remove evidence of assistance. Technical provenance and
review history remain in this document.

| Check | Planned action | Verification | Status |
|---|---|---|---|
| Editorial commentary in the README | Removed the report-editing recap and introduced the analysis directly | Revised README passed no-ai-slop evaluation and independent review | Verified |
| Earlier report problems | Checked tool citations as data sources, template-completion notes, jargon and generic recap prose | Read all notebook Markdown and comments; checked the saved HTML; independent reviewer found no meaningful issues | Verified |
| Required explanations | Retained useful purpose statements, clear headings, decision comments and methodological cautions | Both independent reviewers approved; saved-notebook checks passed | Verified |
| Technical and factual accuracy | Preserved the current notebook, outputs and chart files; reran tests | Notebook, report, analysis and figure hashes unchanged; all 10 tests passed again | Verified |

No claim of AI-free or human-only authorship is made. No stylistic audit can
guarantee grading acceptance or replace the owner's understanding of the work
and compliance with the course's assistance/disclosure rules.

Completed November 4, 2026. The no-ai-slop evaluation was applied to the
reader-facing artifacts, not just to a word scan. Both independent reviewers
found no remaining material writing issues. Required research questions,
headings, useful purpose statements, factual contrasts and causal cautions are
retained because they explain the analysis. Review history, tool provenance
and reproducibility instructions are not erased or treated as evidence of
human-only authorship.

Only README prose changed in this final pass. The previously executed notebook
and HTML were verified unchanged, so no new kernel execution was needed.
The fresh test run passed all 10 tests. The complete local code-comment and
writing revision still awaits a deliberate commit and push.

## Publication authorization

On November 5, 2026, the owner authorized committing and pushing the reviewed
code-comment and writing revision to `main` in the existing public repository.
The report and source files remain identical to the independently reviewed
local artifacts. All 10 tests and the saved-notebook and file-hash checks were
rerun before publication. No further writing changes were requested or made.
The final handoff identifies the remote revision after verification; GitHub
publication does not perform the separate Udacity resubmission.

## Submission checklist review

On November 5, 2026, the owner supplied the project evaluation and submission
checklist and requested another analysis before publication. The checklist
is read alongside the detailed rubric in `../Course Overview.docx`, including
its code, exploration, conclusions and communication criteria. The supplied
checklist's `.ipnyb` is interpreted as the standard `.ipynb` notebook format.

| Requirement | Verification planned | Status |
|---|---|---|
| Choose a curated dataset and identify it | Course no-show dataset identified; local CSV hash matches the exact supplied archive member; report names the source | Meets specifications |
| Pose questions and describe the investigation | Four questions have matching age, delay, SMS and combined analysis sections | Meets specifications |
| Document data wrangling | Missingness/duplicates checked; one negative age and five negative delays excluded; date handling, repeat patients and count audit explained | Meets specifications |
| Provide relevant statistics and plots | Descriptive tables, counts and rates accompany six charts; histograms, bars and a heatmap cover three predictors | Meets specifications |
| Supply HTML/PDF and analysis code | HTML, Investigate_a_Dataset.ipynb and supporting Python files included in SUBMISSION_FILES.txt | Meets specifications |
| Run from start to finish without errors | Rebuilt notebook verified to have no saved outputs, then ran code cells 1-10 in a clean kernel; zero errors, six saved figures, all 10 tests pass | Meets specifications |
| Meet detailed rubric specifications | Both independent reviews approved NumPy/Pandas use, reusable helpers, comments, questions, cleaning, exploration, conclusions, limitations and chart choices | Meets specifications |

Reviewer acceptance cannot be certified in advance. The review records what
the files and execution demonstrate; a final grading decision remains with
Udacity. Both independent reviewers found no blocking gap, completing the
gate for the earlier commit-and-push request. The two reused helpers are called
five times (`group_rates`) and nine times (`label_plot`), and all 10 code cells
contain explanatory comments. Inferential tests and machine learning are
optional in the original assignment and were not added as artificial pass
requirements. Numerical conclusions were independently recomputed, including
the SMS direction reversal in all five shared delay bands.
