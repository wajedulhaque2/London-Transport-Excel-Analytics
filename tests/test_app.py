from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


class DashboardSmokeTest(unittest.TestCase):
    def test_every_page_renders_without_exception(self) -> None:
        app = AppTest.from_file(str(APP), default_timeout=40)
        app.run()
        for page in [
            "Executive dashboard", "Network trends", "Station explorer",
            "Line performance", "Peak flow analysis", "Data notes",
        ]:
            app.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(app.exception), 0, page)

    def test_representative_filters_update_metrics(self) -> None:
        app = AppTest.from_file(str(APP), default_timeout=40)
        app.run()

        app.sidebar.radio[0].set_value("Network trends").run()
        app.sidebar.selectbox[0].set_value(2019).run()
        app.sidebar.selectbox[1].set_value("Weekend").run()
        values = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(values["Tube demand vs 2019"], "100.0%")
        self.assertEqual(values["Bus demand vs 2019"], "100.0%")

        app.sidebar.radio[0].set_value("Station explorer").run()
        app.sidebar.selectbox[0].set_value(2025).run()
        app.sidebar.selectbox[1].set_value("Weekday").run()
        app.sidebar.selectbox[2].set_value("Victoria").run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("of", {metric.label: metric.value for metric in app.metric}["Network rank"])

        app.sidebar.radio[0].set_value("Line performance").run()
        app.sidebar.selectbox[0].set_value("2025-26").run()
        app.sidebar.selectbox[1].set_value("Northern").run()
        values = {metric.label: metric.value for metric in app.metric}
        self.assertNotEqual(values["Actual kilometres"], "Not available")

        app.sidebar.radio[0].set_value("Peak flow analysis").run()
        app.sidebar.selectbox[0].set_value("Evening (19:00–22:00)").run()
        app.sidebar.selectbox[2].set_value("Victoria").run()
        self.assertEqual(len(app.exception), 0)


if __name__ == "__main__":
    unittest.main()
