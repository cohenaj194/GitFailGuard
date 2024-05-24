import unittest
from unittest.mock import patch
from src.log_analyzer import analyze_logs, fetch_logs


class TestLogAnalyzer(unittest.TestCase):
    @patch("src.log_analyzer.requests.get")
    def test_fetch_logs(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "log content"
        logs_url = "http://example.com/logs"
        logs = fetch_logs(logs_url)
        self.assertEqual(logs, "log content")
        mock_get.assert_called_once_with(
            logs_url, headers={"Authorization": "token None"}
        )

    @patch("src.log_analyzer.fetch_logs")
    @patch("openai.Completion.create")
    def test_analyze_logs(self, mock_create, mock_fetch_logs):
        mock_fetch_logs.return_value = "log content"
        mock_create.return_value.choices = [MagicMock(text="analysis result")]
        logs_url = "http://example.com/logs"
        analysis = analyze_logs(logs_url)
        self.assertEqual(analysis, "analysis result")
        mock_fetch_logs.assert_called_once_with(logs_url)
        mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
