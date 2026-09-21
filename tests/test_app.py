from __future__ import annotations

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"


class DashboardSmokeTest(unittest.TestCase):
    def test_every_page_renders_without_exception(self) -> None:
        app = AppTest.from_file(str(APP), default_timeout=30)
        app.run()
        pages = [
            "Executive dashboard",
            "Network trends",
            "Station explorer",
            "Line performance",
            "Peak flow analysis",
            "Data notes",
        ]
        for page in pages:
            app.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(app.exception), 0, page)

    def test_representative_filters_update_metrics(self) -> None:
        app = AppTest.from_file(str(APP), default_timeout=30)
        app.run()

        app.sidebar.radio[0].set_value("Network trends").run()
        app.sidebar.selectbox[0].set_value(2019).run()
        values = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(values["Tube demand vs 2019"], "100.0%")
        self.assertEqual(values["Bus demand vs 2019"], "100.0%")

        app.sidebar.radio[0].set_value("Line performance").run()
        app.sidebar.selectbox[0].set_value("Northern").run()
        values = {metric.label: metric.value for metric in app.metric}
        self.assertEqual(values["Line service rank"], "1")


if __name__ == "__main__":
    unittest.main()
