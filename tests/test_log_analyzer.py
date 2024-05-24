import unittest
from unittest.mock import patch, MagicMock
from src.log_analyzer import (
    analyze_logs,
    fetch_logs,
    extract_info_from_url,
    cleanup_logs,
)


class TestLogAnalyzer(unittest.TestCase):
    @patch("src.log_analyzer.requests.get")
    def test_fetch_logs(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "log content"
        repo_owner = "ff14-advanced-market-search"
        repo_name = "saddlebag-with-pockets"
        run_id = "9182309032"
        job_id = "25250914650"
        logs = fetch_logs(repo_owner, repo_name, run_id, job_id)
        self.assertEqual(logs, "log content")
        mock_get.assert_called_once_with(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/jobs/{job_id}/logs",
            headers={
                "Authorization": "token None",
                "Accept": "application/vnd.github.v3+json",
            },
        )

    @patch("src.log_analyzer.fetch_logs")
    @patch("openai.ChatCompletion.create")
    def test_analyze_logs(self, mock_create, mock_fetch_logs):
        mock_fetch_logs.return_value = "log content"
        mock_create.return_value.choices = [
            MagicMock(message={"content": "analysis result"})
        ]
        logs_url = "https://github.com/ff14-advanced-market-search/saddlebag-with-pockets/actions/runs/9182309032/job/25250914650"
        analysis = analyze_logs(logs_url)
        self.assertEqual(analysis, "analysis result")
        mock_fetch_logs.assert_called_once_with(
            "ff14-advanced-market-search",
            "saddlebag-with-pockets",
            "9182309032",
            "25250914650",
        )
        mock_create.assert_called_once()

    def test_extract_info_from_url(self):
        url = "https://github.com/ff14-advanced-market-search/saddlebag-with-pockets/actions/runs/9182309032/job/25250914650"
        repo_owner, repo_name, run_id, job_id = extract_info_from_url(url)
        self.assertEqual(repo_owner, "ff14-advanced-market-search")
        self.assertEqual(repo_name, "saddlebag-with-pockets")
        self.assertEqual(run_id, "9182309032")
        self.assertEqual(job_id, "25250914650")

    def test_cleanup_logs(self):
        logs = """
        ##[group]Run actions/checkout@v2
        ...
        ##[endgroup]
        ##[group]Run actions/setup-python@v2
        ...
        ##[endgroup]
        ##[error]Process completed with exit code 1.
        """
        cleaned_logs = cleanup_logs(logs, "https://example.com/logs")
        expected_logs = """
        ##[endgroup]
        ##[error]Process completed with exit code 1.
        """
        self.assertEqual(cleaned_logs.strip(), expected_logs.strip())


if __name__ == "__main__":
    unittest.main()
