"""Build the report source; execute it separately with execute_report.py."""

import inspect
import pprint
from pathlib import Path

import nbformat as nbf

import analysis


ROOT = Path(__file__).resolve().parent
raw = analysis.load_appointments()
clean, audit = analysis.clean_appointments(raw)
age = analysis.group_rates(clean, "age_band")
wait = analysis.group_rates(clean, "waiting_band")
sms = analysis.group_rates(clean, "sms_group")
overall = clean.no_show.mean() * 100
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip()))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip()))


md("""
# Appointment no-shows in Brazil

## Introduction

This investigation examines **associations**, rather than causes, between
appointment attendance and three recorded characteristics: age, calendar-day
booking lead time, and SMS receipt. One row represents an appointment; the same
patient can have several appointments. The supplied data contains 110,527
appointments dated April 29–June 8, 2016, from the Brazilian appointment
snapshot supplied by the course. The observation window and clinic population
limit generalization.

The most important reading rule is that **`No-show = Yes` means the patient did
not attend**, whereas `No` means the patient attended. A higher no-show rate
therefore means a larger fraction of appointments were missed.

### Questions

1. How does the distribution of patient age relate to appointment no-show rates?
2. How does calendar-day booking lead time relate to no-show rates?
3. How do the size and no-show rate of the two recorded SMS groups compare?
4. Does the overall SMS comparison persist within lead-time bands, and how do
   age and lead time jointly describe the outcome?

The outcome is a binary appointment-level no-show indicator. The three primary
explanatory variables are age, lead time and SMS receipt. No prediction model,
causal estimate, or significance test is attempted.

### Report navigation

- [Data description and setup](#data-description)
- [Data wrangling](#data-wrangling)
- [Exploratory data analysis](#exploratory-data-analysis)
- [Conclusions](#conclusions)
- [Limitations](#limitations)

<a id="data-description"></a>
### Data description

| Source field | Meaning and use |
|---|---|
| PatientId | Patient identifier; used only to count repeated patients, not as a predictor |
| AppointmentID | Appointment identifier; used to check record uniqueness |
| Gender | Recorded gender; retained as context, not a primary predictor |
| ScheduledDay | Timestamp when the appointment was scheduled |
| AppointmentDay | Appointment date; time of attendance is not supplied |
| Age | Recorded age in years, including infants aged zero |
| Neighbourhood | Recorded clinic/appointment neighbourhood |
| Scholarship | Recorded welfare-program enrollment indicator |
| Hipertension | Recorded hypertension flag; source spelling retained in this dictionary |
| Diabetes | Recorded diabetes flag |
| Alcoholism | Recorded alcoholism flag |
| Handcap | Recorded handicap level; values need not be binary |
| SMS_received | Recorded SMS flag (0 or 1); timing and delivery process are not documented |
| No-show | Recorded attendance label: Yes = missed, No = attended |

The project-provided CSV is the analysis source. The course links the
[original dataset description](https://www.kaggle.com/datasets/joniarroba/noshowappointments).
This report uses only the supplied snapshot. Patient/appointment identifiers
are not displayed in previews or included in the HTML as row-level records.
""")

code("""
from pathlib import Path
import hashlib
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from IPython.display import display
%matplotlib inline

plt.rcParams.update({
    'figure.dpi': 115, 'font.size': 10, 'axes.titlesize': 12,
    'axes.labelsize': 10, 'figure.facecolor': 'white', 'axes.facecolor': 'white',
})
FIGURES = Path('figures')
FIGURES.mkdir(exist_ok=True)
DATA = Path('data/noshowappointments-kagglev2-may-2016.csv')
EXPECTED_SHA256 = '9132d3e7d0246617df9041d3764f20ad6f08e7b0d9f0997fa254fc5e52eda27d'
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == EXPECTED_SHA256
print(f'Python {sys.version.split()[0]} | pandas {pd.__version__} | NumPy {np.__version__} | matplotlib {matplotlib.__version__}')
print('Supplied dataset checksum verified.')
""")

md("""
<a id="data-wrangling"></a>
## Data Wrangling

### Inspect before changing data

Read identifiers as strings to preserve their source representation. Inspect
shape, datatypes, missingness, duplicate appointments, distributions and date
coverage before choosing cleaning rules. Preview only non-identifier fields.
These checks establish what must be cleaned, rather than assuming the dataset
is already suitable for analysis.
""")

code("""
raw = pd.read_csv(DATA, dtype={'PatientId': 'string', 'AppointmentID': 'string'})
print('Rows and columns:', raw.shape)
display(raw.drop(columns=['PatientId', 'AppointmentID']).head())
display(pd.DataFrame({'dtype': raw.dtypes.astype(str), 'missing': raw.isna().sum(),
                      'distinct': raw.nunique(dropna=False)}))
display(raw[['Age', 'SMS_received']].describe())
print('Exact duplicate rows:', int(raw.duplicated().sum()))
print('Duplicate appointment IDs:', int(raw['AppointmentID'].duplicated().sum()))
print('Unique patient identifiers:', raw['PatientId'].nunique())
print("Additional rows after each patient's first appointment:", int(raw['PatientId'].duplicated().sum()))
display(raw['No-show'].value_counts().rename('appointments').to_frame())
""")

md("""
### Cleaning decisions

The raw file has no missing values, no exact duplicate rows, and unique
appointment IDs. It does contain one negative age and five appointment dates
before the scheduling date. These six records are excluded from a common
analysis cohort so that comparisons use consistent denominators. Negative
lead times could represent errors or undocumented changes; their meaning
cannot be resolved here. No values are imputed.

Convert dates with explicit UTC parsing. Because appointment time is not
available, normalize **both** date fields to their encoded calendar dates
before subtraction: a same-day appointment must have a lead time of zero even
if its scheduling timestamp is in the afternoon. This measures calendar-day
lead time, not elapsed hours; the original local timezone is not reconstructed.

Keep age zero and high nonnegative ages, including 115, because the source
does not justify an arbitrary upper-age cutoff. Age bands isolate broad
patterns without asserting a linear relationship. Retain repeat appointments
for a patient because the unit is the appointment. Do not treat those records
as independent people. Rename fields for readability; keep `Handcap` as a
level rather than collapsing its multiple values into a binary variable.

The reusable cleaning and group-rate functions below are also tested in
`tests/test_analysis.py`. Every exclusion is recorded sequentially, so the
removed counts sum exactly to the change in cohort size.
""")

helper_source = "SOURCE_COLUMNS = " + pprint.pformat(analysis.SOURCE_COLUMNS, sort_dicts=False)
helper_source += "\n\n" + inspect.getsource(analysis.clean_appointments)
helper_source += "\n\n" + inspect.getsource(analysis.group_rates)
helper_source += "\n\n" + inspect.getsource(analysis.label_plot)
helper_source += "\nprint('Reusable cleaning, rate-table and plot-label helpers defined.')"
code(helper_source)

code("""
appointments, cleaning_audit = clean_appointments(raw)
display(cleaning_audit)
assert len(raw) - cleaning_audit['removed'].sum() == len(appointments)
assert appointments['appointment_id'].is_unique
assert appointments['age'].ge(0).all() and appointments['waiting_days'].ge(0).all()
assert not appointments[['age_band', 'waiting_band', 'sms_group']].isna().any().any()
print('Clean cohort:', len(appointments), 'appointments')
print('Unique patients:', appointments['patient_id'].nunique())
print('Appointment dates:', appointments['appointment_day'].min().date(), 'to', appointments['appointment_day'].max().date())
display(appointments[['age', 'waiting_days']].describe(percentiles=[.25, .5, .75, .95]))
display(appointments[['gender', 'age', 'waiting_days', 'sms_group', 'no_show']].head())
""")

md(f"""
**Cleaning result.** Exactly {len(raw)-len(clean):,} appointments are excluded,
leaving **{len(clean):,} appointments from {clean.patient_id.nunique():,} distinct
patient identifiers**. There are {int(clean.no_show.sum()):,} missed appointments
in this cohort: **{overall:.2f}%** of all retained appointments. The six excluded
records are too few to dominate overall percentages, but their removal remains
explicit. The data covers scheduled appointments, not all care needs or all
people in the covered population.
""")

md("""
<a id="exploratory-data-analysis"></a>
## Exploratory Data Analysis

### 1. Age and appointment attendance

First inspect the outcome balance and age distribution separately. Then compare
no-show rates across age groups. Counts measure workload; rates measure the
fraction missed, so these answer different questions. Group-rate tables retain
both numerators and denominators to avoid mistaking a large group for a high-risk
group. Bands are fixed descriptive choices, not learned thresholds.
""")

code("""
overall_pct = 100 * appointments['no_show'].mean()
outcome_counts = appointments['no_show'].map({False: 'Attended', True: 'Missed'}).value_counts().reindex(['Attended', 'Missed'])
display(outcome_counts.rename('appointments').to_frame())
age_rates = group_rates(appointments, 'age_band')
display(age_rates.round(2))
fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
outcome_counts.plot.bar(ax=axes[0], color=['#26736b', '#c2673d'], rot=0)
label_plot(axes[0], 'Most retained appointments were attended', 'Recorded attendance', 'Appointments')
appointments['age'].plot.hist(ax=axes[1], bins=np.arange(0, 121, 5), color='#4b75a8', edgecolor='white')
label_plot(axes[1], 'Appointment ages span infants through older adults', 'Age (years)', 'Appointments')
fig.savefig(FIGURES / '01_outcome_and_age.png', bbox_inches='tight')
plt.show()

fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
age_rates['no_show_pct'].plot.bar(ax=ax, color='#4b75a8', rot=0)
ax.axhline(overall_pct, color='#a54e2a', linestyle='--', label=f'Overall {overall_pct:.2f}%')
ax.set_ylim(0, 30)
ax.yaxis.set_major_formatter(PercentFormatter(100))
label_plot(ax, 'No-show rate is highest in the 18-34 age band', 'Age band (years)', 'Missed appointments (%)')
ax.legend()
fig.savefig(FIGURES / '02_age_rates.png', bbox_inches='tight')
plt.show()
""")

md(f"""
**Finding.** The no-show rate is {age.loc['18-34', 'no_show_pct']:.2f}% for
ages 18–34 and {age.loc['65+', 'no_show_pct']:.2f}% for ages 65 and above.
Under-18 appointments have a rate of {age.loc['Under 18', 'no_show_pct']:.2f}%.
Thus the pattern is not simply that the youngest patients miss the most
appointments. These are appointment-weighted associations; age can also relate
to medical need, transport, caregiver support and appointment lead time, none
of which are held constant in this first comparison.
""")

md("""
### 2. Booking lead time and attendance

Inspect the full lead-time distribution, including its long tail, and then
compare rates in explicit calendar-day intervals. Same-day appointments are
shown separately because they have substantially less opportunity for plans to
change. The grouped rate plot complements the histogram; a histogram alone
cannot show whether a group has a higher probability of missing an appointment.
""")

code("""
waiting_rates = group_rates(appointments, 'waiting_band')
display(waiting_rates.round(2))
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5), constrained_layout=True)
appointments['waiting_days'].plot.hist(ax=axes[0], bins=np.arange(0, 186, 5), color='#26736b', edgecolor='white')
label_plot(axes[0], 'Lead times are concentrated near the booking date', 'Calendar-day lead time', 'Appointments')
waiting_rates['no_show_pct'].plot.bar(ax=axes[1], color='#26736b', rot=30)
axes[1].axhline(overall_pct, color='#a54e2a', linestyle='--', label='Overall rate')
axes[1].set_ylim(0, 40)
axes[1].yaxis.set_major_formatter(PercentFormatter(100))
label_plot(axes[1], 'Same-day appointments have a much lower no-show rate', 'Lead-time band', 'Missed appointments (%)')
axes[1].legend()
fig.savefig(FIGURES / '03_lead_time.png', bbox_inches='tight')
plt.show()
""")

md(f"""
**Finding.** Same-day appointments have a no-show rate of
{wait.loc['Same day','no_show_pct']:.2f}%, compared with
{wait.loc['1-7 days','no_show_pct']:.2f}% at 1–7 days and
{wait.loc['31-60 days','no_show_pct']:.2f}% at 31–60 days.
The 61+ day group falls to {wait.loc['61+ days','no_show_pct']:.2f}%, so this
relationship is not strictly increasing throughout the range. Group sizes and
case mix differ. The pattern describes the recorded scheduling process; it
does not prove that moving an appointment earlier would change attendance.
""")

md("""
### 3. Recorded SMS receipt and attendance

Inspect the number of appointments in each SMS group before comparing rates.
The flag means an SMS was recorded; the dataset does not identify the time of
the message, whether it was read, or why one patient received a message and
another did not. Treat both groups as observational cohorts, not experimental
treatment and control groups.
""")

code("""
sms_rates = group_rates(appointments, 'sms_group')
display(sms_rates.round(2))
display(appointments.groupby('sms_group', observed=True)['waiting_days'].agg(['median', 'mean']).round(2))
fig, axes = plt.subplots(1, 2, figsize=(12, 4), constrained_layout=True)
sms_rates['appointments'].plot.bar(ax=axes[0], rot=0, color=['#4b75a8', '#c2673d'])
label_plot(axes[0], 'The two recorded SMS groups have different sizes', 'Recorded SMS flag', 'Appointments')
sms_rates['no_show_pct'].plot.bar(ax=axes[1], rot=0, color=['#4b75a8', '#c2673d'])
axes[1].set_ylim(0, 35)
axes[1].yaxis.set_major_formatter(PercentFormatter(100))
label_plot(axes[1], 'The crude SMS comparison is not an intervention estimate', 'Recorded SMS flag', 'Missed appointments (%)')
fig.savefig(FIGURES / '04_sms_crude.png', bbox_inches='tight')
plt.show()
""")

md(f"""
**Finding.** The overall no-show rate is
{sms.loc['SMS recorded','no_show_pct']:.2f}% among appointments with an SMS
recorded ({int(sms.loc['SMS recorded','appointments']):,} appointments), compared
with {sms.loc['No SMS recorded','no_show_pct']:.2f}% without one
({int(sms.loc['No SMS recorded','appointments']):,} appointments).
This crude comparison cannot establish that reminders worsen attendance.
Booking lead time differs between these cohorts and provides a concrete
reason to inspect group composition before drawing conclusions.
""")

md("""
### 4. Comparisons within lead-time bands and across age groups

Use the same lead-time bands for both SMS groups and retain every observed
denominator. An absent category is not a zero no-show rate: the same-day/SMS
combination has no observations. Its plot value is therefore missing. The
second plot compares age and lead time jointly; it shows where an apparent
age relationship coexists with differences in scheduling delay.
""")

code("""
sms_by_wait = group_rates(appointments, ['waiting_band', 'sms_group'])
display(sms_by_wait.round(2))
rate_matrix = sms_by_wait['no_show_pct'].unstack('sms_group')
count_matrix = sms_by_wait['appointments'].unstack('sms_group')
display(count_matrix)
fig, ax = plt.subplots(figsize=(11, 4.5), constrained_layout=True)
rate_matrix.plot.bar(ax=ax, rot=25, color=['#4b75a8', '#c2673d'])
ax.set_ylim(0, 45)
ax.yaxis.set_major_formatter(PercentFormatter(100))
label_plot(ax, 'Within shared lead-time bands, the SMS comparison reverses', 'Lead-time band (absent group is not zero)', 'Missed appointments (%)')
ax.legend(title='Recorded SMS flag')
fig.savefig(FIGURES / '05_sms_by_lead_time.png', bbox_inches='tight')
plt.show()

joint = group_rates(appointments, ['age_band', 'waiting_band'])
display(joint.round(2))
joint_rates = joint['no_show_pct'].unstack('waiting_band')
joint_counts = joint['appointments'].unstack('waiting_band')
fig, ax = plt.subplots(figsize=(11, 5), constrained_layout=True)
shown = joint_rates.where(joint_counts >= 100)
image = ax.imshow(shown.to_numpy(), cmap='YlGnBu', vmin=0, vmax=45, aspect='auto')
ax.set_xticks(np.arange(len(shown.columns)), labels=shown.columns, rotation=25)
ax.set_yticks(np.arange(len(shown.index)), labels=shown.index)
for row in range(len(shown.index)):
    for col in range(len(shown.columns)):
        value = shown.iloc[row, col]
        n = joint_counts.iloc[row, col]
        label = f'{value:.1f}%\\nn={int(n):,}' if pd.notna(value) else f'n={int(n):,} <100'
        ax.text(col, row, label, ha='center', va='center', fontsize=8,
                color='white' if pd.notna(value) and value > 30 else 'black')
label_plot(ax, 'Age and lead time jointly describe different attendance patterns', 'Lead-time band', 'Age band (years)')
ax.grid(False)
fig.colorbar(image, ax=ax, label='Missed appointments (%)')
fig.savefig(FIGURES / '06_age_by_lead_time.png', bbox_inches='tight')
plt.show()
""")

md("""
**Finding.** Among all five lead-time bands where both SMS groups are observed,
the SMS-recorded group has a lower no-show rate than the no-SMS-recorded group.
There are no SMS-recorded appointments in the same-day band, which itself has
a very low no-show rate. Its inclusion in the no-SMS cohort partly explains
why the overall comparison runs in the opposite direction. This is an example
of an aggregated comparison changing after stratification, not proof of a
reminder effect. The bands are broad, other factors still differ, and SMS
timing is unknown. The age-by-lead-time table and heatmap further show that
comparing only one characteristic hides considerable variation.

Cells with fewer than 100 appointments are withheld from the heatmap's color
scale as a display convention, not as a statistical significance rule. All
observed counts and rates remain available in the table above.
""")

md(f"""
<a id="conclusions"></a>
## Conclusions

In the cleaned snapshot, **{int(clean.no_show.sum()):,} of {len(clean):,}
appointments were missed ({overall:.2f}%)**.

- **Age:** the 18–34 group has a higher descriptive no-show rate
  ({age.loc['18-34','no_show_pct']:.2f}%) than the 65+ group
  ({age.loc['65+','no_show_pct']:.2f}%). Age alone does not explain attendance.
- **Lead time:** same-day appointments have a much lower rate
  ({wait.loc['Same day','no_show_pct']:.2f}%) than appointments booked 31–60
  calendar days ahead ({wait.loc['31-60 days','no_show_pct']:.2f}%). The pattern
  is not monotonic in the longest-delay band.
- **SMS:** the crude SMS association reverses within every shared lead-time
  band. Comparing the overall SMS percentages without considering scheduling
  differences would be misleading.

These findings answer the initial questions descriptively. They motivate
collecting richer scheduling and communication data and evaluating reminder
policies with an appropriate design; they do not justify changing clinical or
administrative policy on their own.

<a id="limitations"></a>
## Limitations and useful next steps

1. **Observational assignment and unknown SMS timing.** Neither SMS receipt nor
   lead time was randomized. Delivery timing, reading, appointment urgency and
   selection into reminders are unobserved. A causal evaluation would need a
   prospective design or defensible identification assumptions and richer data.
2. **Repeated patients.** The {len(clean):,} appointments represent only
   {clean.patient_id.nunique():,} distinct identifiers. Frequent attendees have
   more weight in appointment-level rates. No inferential intervals or
   independence-based significance claims are made; patient-level or clustered
   analyses would be useful for a different research question.
3. **Limited population and time coverage.** This is a limited clinic population's
   short 2016 appointment window. Results do not describe all of Brazil or current
   services. Wider time coverage and the data-collection rules would help.
4. **Measurement and exclusions.** Dates supply calendar-day lead time, not
   exact appointment times. Six invalid records were excluded; very high ages
   were retained. The snapshot does not explain corrections, cancellations,
   rescheduling or the appointment-labeling process.
5. **Unmeasured factors and grouping choices.** Transport, appointment purpose,
   urgency, work schedules and provider characteristics could matter. Age and
   lead-time bins lose information and are not a complete adjustment for
   confounding. Sensitivity to different bins, continuous-variable summaries
   and an explicit patient-level study would be useful follow-ups.

## Reproducibility and references

The required input is `data/noshowappointments-kagglev2-may-2016.csv`; its SHA-256
is verified at the start. All tables and figures are recomputed from that
snapshot. The notebook's cleaning and plotting helpers are embedded here, so
it can run without importing project-specific modules. Raw input data is
excluded from the submission; retrieval instructions are in the README.

- Udacity, *Course Overview*, supplied project instructions and rubric.
- Joni Hoppen, *Medical Appointment No Shows*, Kaggle, source description linked
  by the course. The analysis uses the course-supplied snapshot.
- Pandas documentation: datetime conversion, categorical grouping and named
  aggregation; API usage checked through Context7.

The original template tips have been replaced with the project's analysis and
explanations. No statistical test, predictive model or causal estimate is
claimed in this report.
""")

nb = nbf.v4.new_notebook(cells=cells)
nb.metadata.update({
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.13"},
})
nbf.write(nb, ROOT / "Investigate_a_Dataset.ipynb")
print(f"Built {len(cells)} cells; execute and inspect the saved notebook next.")
