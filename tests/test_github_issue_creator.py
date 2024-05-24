import unittest
from unittest.mock import patch
from src.github_issue_creator import create_github_issue


class TestGitHubIssueCreator(unittest.TestCase):
    @patch("src.github_issue_creator.requests.post")
    def test_create_github_issue(self, mock_post):
        mock_post.return_value.status_code = 201
        repo_name = "test/repo"
        workflow_name = "Test Workflow"
        logs_url = "http://example.com/logs"
        analysis = "analysis result"
        create_github_issue(repo_name, workflow_name, logs_url, analysis)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("https://api.github.com/repos/test/repo/issues", args)
        self.assertEqual(kwargs["headers"]["Authorization"], "token None")
        self.assertEqual(kwargs["json"]["title"], "Failed GitHub Action: Test Workflow")
        self.assertIn(
            "The GitHub Action `Test Workflow` failed.", kwargs["json"]["body"]
        )
        self.assertIn(
            "Logs: [View Logs](http://example.com/logs)", kwargs["json"]["body"]
        )
        self.assertIn("Analysis:\nanalysis result", kwargs["json"]["body"])


if __name__ == "__main__":
    unittest.main()
