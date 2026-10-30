import unittest
from pathlib import Path
import sys
import hashlib
import io
import runpy
import tempfile
from unittest.mock import patch
from urllib.error import HTTPError

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def sample_data():
    return pd.DataFrame({
        "PatientId": ["p1", "p2", "p3", "p4"],
        "AppointmentID": ["a1", "a2", "a3", "a4"],
        "Age": [0, 30, 70, 115],
        "ScheduledDay": ["2016-05-01T12:00:00Z"] * 4,
        "AppointmentDay": ["2016-05-01T00:00:00Z", "2016-05-04T00:00:00Z",
                           "2016-05-11T00:00:00Z", "2016-06-15T00:00:00Z"],
        "SMS_received": [0, 1, 1, 0],
        "No-show": ["No", "Yes", "No", "Yes"],
    })


class CleaningTests(unittest.TestCase):
    def test_calendar_days_and_outcome_are_encoded_correctly(self):
        import analysis
        clean, audit = analysis.clean_appointments(sample_data())
        self.assertEqual(clean["waiting_days"].tolist(), [0, 3, 10, 45])
        self.assertEqual(clean["no_show"].tolist(), [False, True, False, True])
        self.assertEqual(clean["age"].tolist(), [0, 30, 70, 115])
        self.assertEqual(int(audit.iloc[-1]["remaining"]), 4)

    def test_exclusion_accounting_preserves_repeated_patients(self):
        import analysis
        raw = sample_data()
        raw.loc[1, "PatientId"] = "p1"
        invalid_age = raw.iloc[[0]].assign(AppointmentID="bad_age", Age=-1)
        invalid_wait = raw.iloc[[0]].assign(AppointmentID="bad_wait", AppointmentDay="2016-04-30T00:00:00Z")
        missing_age = raw.iloc[[0]].assign(AppointmentID="missing_age", Age=np.nan)
        raw = pd.concat([raw, raw.iloc[[0]], invalid_age, invalid_wait, missing_age], ignore_index=True)
        clean, audit = analysis.clean_appointments(raw)
        self.assertEqual(len(clean), 4)
        self.assertEqual(clean["patient_id"].nunique(), 3)
        self.assertEqual(int(audit["removed"].sum()), 4)
        self.assertEqual(len(raw) - int(audit["removed"].sum()), len(clean))

    def test_unknown_outcome_is_rejected(self):
        import analysis
        raw = sample_data()
        raw.loc[0, "No-show"] = "Unknown"
        with self.assertRaisesRegex(ValueError, "No-show"):
            analysis.clean_appointments(raw)

    def test_conflicting_duplicate_appointment_ids_are_rejected(self):
        import analysis
        raw = sample_data()
        raw.loc[1, "AppointmentID"] = "a1"
        with self.assertRaisesRegex(ValueError, "appointment"):
            analysis.clean_appointments(raw)


class SummaryTests(unittest.TestCase):
    def test_rate_table_keeps_denominators_and_observed_groups(self):
        import analysis
        clean, _ = analysis.clean_appointments(sample_data())
        rates = analysis.group_rates(clean, "sms_received")
        self.assertEqual(rates["appointments"].tolist(), [2, 2])
        self.assertEqual(rates["no_shows"].tolist(), [1, 1])
        self.assertTrue(np.allclose(rates["no_show_pct"], [50, 50]))

    def test_every_valid_record_gets_an_age_and_waiting_band(self):
        import analysis
        clean, _ = analysis.clean_appointments(sample_data())
        self.assertFalse(clean[["age_band", "waiting_band"]].isna().any().any())
        self.assertEqual(str(clean.iloc[0]["waiting_band"]), "Same day")
        self.assertEqual(str(clean.iloc[-1]["age_band"]), "65+")

    def test_plot_helper_returns_labeled_axes(self):
        import analysis
        from matplotlib import pyplot as plt
        ax = analysis.label_plot(plt.subplots()[1], "Example", "Group", "Rate (%)")
        self.assertEqual((ax.get_title(), ax.get_xlabel(), ax.get_ylabel()),
                         ("Example", "Group", "Rate (%)"))
        plt.close("all")


class DataRetrievalTests(unittest.TestCase):
    def test_download_uses_verified_mirror_when_course_url_is_forbidden(self):
        import analysis
        content = b"fixture CSV contents\n"
        forbidden = HTTPError("https://course.example/data.csv", 403, "Forbidden", {}, None)
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "data/appointments.csv"
            with patch.object(analysis, "DATA_FILE", destination), patch.object(
                analysis, "DATA_SHA256", hashlib.sha256(content).hexdigest()
            ), patch("sys.argv", ["prepare_data.py", "--download"]), patch(
                "urllib.request.urlopen", side_effect=[forbidden, io.BytesIO(content)]
            ) as fetch:
                runpy.run_path(str(Path(__file__).resolve().parents[1] / "prepare_data.py"), run_name="__main__")
            self.assertEqual(destination.read_bytes(), content)
            self.assertEqual(fetch.call_count, 2)


if __name__ == "__main__":
    unittest.main()
