import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.pipeline import run_full_pipeline
from src.scraper import download_all_sources


class AutoscrapParameterTests(unittest.TestCase):
    @patch("src.pipeline.run_enso_backtesting")
    @patch("src.pipeline.download_all_sources")
    def test_autoscrap_false_uses_local_data_without_scraping(
        self,
        mock_download,
        mock_backtesting,
    ):
        mock_backtesting.return_value = {"status": "success", "metrics": {}}

        report = run_full_pipeline(
            horizons=(1,),
            epochs=1,
            autoscrap=False,
            prepare_data=False,
            run_eda=False,
        )

        # Scrapers MUST NOT be called when autoscrap is False
        mock_download.assert_not_called()
        mock_backtesting.assert_called_once()
        self.assertNotIn("autoscrap_summary", report)

    @patch("src.pipeline.run_enso_backtesting")
    @patch("src.pipeline.run_data_preprocessing")
    @patch("src.pipeline.download_all_sources")
    def test_autoscrap_true_triggers_all_downloads_before_qc(
        self,
        mock_download,
        mock_preprocessing,
        mock_backtesting,
    ):
        mock_download.return_value = {"oni": "ok", "soi": "ok", "dmi": "ok"}
        mock_backtesting.return_value = {"status": "success", "metrics": {}}

        report = run_full_pipeline(
            horizons=(1,),
            epochs=1,
            autoscrap=True,
            prepare_data=False,
            run_eda=False,
        )

        # Scrapers MUST be called when autoscrap is True
        mock_download.assert_called_once()
        mock_preprocessing.assert_called_once()
        mock_backtesting.assert_called_once()
        self.assertIn("autoscrap_summary", report)


if __name__ == "__main__":
    unittest.main()
