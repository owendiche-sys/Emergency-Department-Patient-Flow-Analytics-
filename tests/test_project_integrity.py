"""Lightweight integrity checks that run with the Python standard library."""

from __future__ import annotations

import ast
import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"


class ProjectIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with DATA_PATH.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            cls.rows = list(reader)
            cls.columns = reader.fieldnames or []

    def test_clean_data_dimensions_and_ids(self) -> None:
        self.assertEqual(len(self.rows), 16_025)
        self.assertEqual(len(self.columns), 39)
        self.assertEqual(len({row["visit_id"] for row in self.rows}), 16_025)

    def test_wait_flags_match_documented_thresholds(self) -> None:
        valid_rows = [row for row in self.rows if row["wait_time_minutes"] != "NULL"]
        self.assertEqual(len(valid_rows), 13_272)
        two_hour = sum(int(row["extended_wait_2hr_flag"]) for row in valid_rows)
        four_hour = sum(int(row["long_wait_4hr_flag"]) for row in valid_rows)
        self.assertEqual(two_hour, 907)
        self.assertEqual(four_hour, 238)
        self.assertTrue(
            all(
                int(row["extended_wait_2hr_flag"]) == (float(row["wait_time_minutes"]) >= 120)
                and int(row["long_wait_4hr_flag"]) == (float(row["wait_time_minutes"]) > 240)
                for row in valid_rows
            )
        )

    def test_python_and_notebook_sources_parse(self) -> None:
        for path in ROOT.glob("**/*.py"):
            if ".git" not in path.parts and ".venv" not in path.parts:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for path in (ROOT / "notebooks").glob("*.ipynb"):
            notebook = json.loads(path.read_text(encoding="utf-8"))
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    compile("".join(cell["source"]), str(path), "exec")

    def test_sql_uses_final_column_and_threshold_definitions(self) -> None:
        kpis = (ROOT / "sql" / "04_kpi_queries.sql").read_text(encoding="utf-8")
        views = (ROOT / "sql" / "05_views_for_python.sql").read_text(encoding="utf-8")
        self.assertNotIn("pain_score", kpis)
        self.assertEqual(views.count("CREATE OR REPLACE VIEW vw_ed_patient_flow_summary"), 1)
        self.assertIn("extended_wait_2hr_flag", views)
        self.assertIn("long_wait_4hr_flag", views)

    def test_final_model_outputs_and_dashboard_language(self) -> None:
        metrics_path = ROOT / "outputs" / "models" / "wait_prediction_model_metrics.csv"
        target_path = ROOT / "outputs" / "models" / "wait_target_balance.csv"
        self.assertTrue(metrics_path.exists())
        self.assertTrue(target_path.exists())
        dashboard = (ROOT / "dashboard" / "app.py").read_text(encoding="utf-8").lower()
        self.assertNotIn("placeholder", dashboard)
        self.assertNotIn("week 4", dashboard)
        self.assertNotIn("week 5", dashboard)


if __name__ == "__main__":
    unittest.main()
