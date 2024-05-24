import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from src.webhook_handler import webhook


class TestWebhookHandler(unittest.TestCase):
    @patch("src.webhook_handler.request")
    @patch("src.webhook_handler.create_github_issue")
    @patch("src.webhook_handler.analyze_logs")
    def test_webhook(self, mock_analyze_logs, mock_create_github_issue, mock_request):
        app = Flask(__name__)
        with app.test_request_context(
            "/webhook",
            json={
                "action": "completed",
                "workflow_run": {
                    "conclusion": "failure",
                    "name": "Test Workflow",
                    "logs_url": "http://example.com/logs",
                },
                "repository": {"full_name": "test/repo"},
            },
        ):
            mock_analyze_logs.return_value = "Mock analysis"
            response = webhook()
            self.assertEqual(response[1], 200)
            mock_analyze_logs.assert_called_once_with("http://example.com/logs")
            mock_create_github_issue.assert_called_once_with(
                "test/repo", "Test Workflow", "http://example.com/logs", "Mock analysis"
            )


if __name__ == "__main__":
    unittest.main()
