"""Small, reusable transformations for the appointment-level investigation."""

from pathlib import Path

import numpy as np
import pandas as pd


DATA_FILE = Path(__file__).parent / "data/noshowappointments-kagglev2-may-2016.csv"
DATA_SHA256 = "9132d3e7d0246617df9041d3764f20ad6f08e7b0d9f0997fa254fc5e52eda27d"

SOURCE_COLUMNS = {
    "PatientId": "patient_id", "AppointmentID": "appointment_id",
    "Gender": "gender", "ScheduledDay": "scheduled_day",
    "AppointmentDay": "appointment_day", "Age": "age",
    "Neighbourhood": "neighbourhood", "Scholarship": "scholarship",
    "Hipertension": "hypertension", "Diabetes": "diabetes",
    "Alcoholism": "alcoholism", "Handcap": "handicap_level",
    "SMS_received": "sms_received", "No-show": "no_show_label",
}


def load_appointments(path=DATA_FILE):
    return pd.read_csv(path, dtype={"PatientId": "string", "AppointmentID": "string"})


def clean_appointments(raw):
    """Return one row per usable appointment and sequential exclusion counts."""
    required = {"PatientId", "AppointmentID", "Age", "ScheduledDay",
                "AppointmentDay", "SMS_received", "No-show"}
    if not required.issubset(raw.columns):
        raise ValueError(f"Missing required columns: {sorted(required - set(raw.columns))}")
    labels = set(raw["No-show"].dropna().unique())
    if not labels.issubset({"Yes", "No"}):
        raise ValueError(f"Unexpected No-show labels: {labels}")

    df = raw.rename(columns=SOURCE_COLUMNS).copy()
    audit = [{"rule": "Input appointments", "removed": 0, "remaining": len(df)}]

    def exclude(mask, reason):
        nonlocal df
        removed = int(mask.sum())
        df = df.loc[~mask].copy()
        audit.append({"rule": reason, "removed": removed, "remaining": len(df)})

    exclude(df.duplicated(), "Exact duplicate rows")
    if df["appointment_id"].duplicated().any():
        raise ValueError("Conflicting duplicate appointment IDs require investigation")
    for column in ["scheduled_day", "appointment_day"]:
        df[column] = pd.to_datetime(df[column], utc=True, errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["sms_received"] = pd.to_numeric(df["sms_received"], errors="coerce")
    critical = ["patient_id", "appointment_id", "age", "scheduled_day",
                "appointment_day", "sms_received", "no_show_label"]
    exclude(df[critical].isna().any(axis=1), "Missing or unparseable critical fields")
    if not df["sms_received"].isin([0, 1]).all():
        raise ValueError("Unexpected SMS_received values")
    exclude(df["age"] < 0, "Negative ages")

    # Appointment timestamps omit appointment time; compare encoded calendar dates.
    df["waiting_days"] = (
        df["appointment_day"].dt.normalize() - df["scheduled_day"].dt.normalize()
    ).dt.days
    exclude(df["waiting_days"] < 0, "Appointment precedes scheduling date")
    df["no_show"] = df["no_show_label"].eq("Yes")
    df["age_band"] = pd.cut(
        df["age"], [0, 18, 35, 50, 65, np.inf], right=False,
        labels=["Under 18", "18-34", "35-49", "50-64", "65+"],
    )
    df["waiting_band"] = pd.cut(
        df["waiting_days"], [-1, 0, 7, 14, 30, 60, np.inf],
        labels=["Same day", "1-7 days", "8-14 days", "15-30 days", "31-60 days", "61+ days"],
    )
    df["sms_group"] = pd.Categorical(
        df["sms_received"].map({0: "No SMS recorded", 1: "SMS recorded"}),
        categories=["No SMS recorded", "SMS recorded"], ordered=True,
    )
    return df.reset_index(drop=True), pd.DataFrame(audit)


def group_rates(df, columns):
    """Keep denominators alongside observed group rates; empty groups stay absent."""
    result = df.groupby(columns, observed=True, dropna=False)["no_show"].agg(
        appointments="size", no_shows="sum", no_show_rate="mean",
    )
    return result.assign(no_show_pct=lambda x: 100 * x["no_show_rate"])


def label_plot(ax, title, xlabel, ylabel):
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.2)
    return ax
