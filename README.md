# GitFailGuard

<p align="center">
  <img src="https://github.com/cohenaj194/GitFailGuard/assets/17516896/ab1733a6-dff9-46aa-a909-2ac27f18ad0d" width="200">
</p>

<!-- ![GitFailGuard](https://github.com/cohenaj194/GitFailGuard/assets/17516896/ab1733a6-dff9-46aa-a909-2ac27f18ad0d) -->

GitFailGuard is an AI-powered tool that automatically reviews failed GitHub Actions and creates detailed GitHub Issues to help you quickly address problems.

## Features

- Automated detection of failed GitHub Actions.
- AI-powered log analysis to identify potential causes of failure.
- Automatic creation of GitHub Issues with detailed failure information.

### Example

https://github.com/ff14-advanced-market-search/saddlebag-with-pockets/issues/431

## Setup

### Prerequisites

- Docker and Docker Compose
- GitHub token with appropriate permissions
- OpenAI API key

### Environment Variables

Ensure you have the following environment variables set:

- `GITHUB_TOKEN`: Your GitHub token.
- `OPENAI_API_KEY`: Your OpenAI API key.

You can set these variables in your shell:

```bash
export GITHUB_TOKEN=your_github_token_here
export OPENAI_API_KEY=your_openai_api_key_here
```

### Running with Docker Compose

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/GitFailGuard.git
    cd GitFailGuard
    ```

2. Create a `.env` file in the root directory and add your environment variables:

    ```bash
    GITHUB_TOKEN=your_github_token_here
    OPENAI_API_KEY=your_openai_api_key_here
    ```

3. Build and run the application:

    ```bash
    docker-compose up --build
    ```

4. Verify the application is running:

    Open a browser and navigate to `http://localhost:5000` to see if the application is up and running.

### Testing the Webhook

You can test the action response webhook endpoint using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "action": "completed",
  "workflow_job": {
    "conclusion": "failure",
    "name": "Test Workflow",
    "logs_url": "https://github.com/ff14-advanced-market-search/saddlebag-with-pockets/actions/runs/9182309032/job/25250914650"
  },
  "repository": {
    "full_name": "ff14-advanced-market-search/saddlebag-with-pockets"
  }
}' http://127.0.0.1:5000/webhook
```

You can test the issue comment response webhook endpoint using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "action": "created",
  "issue": {
    "number": 92
  },
  "comment": {
    "body": "Cause of Failure: The error occurred because the required version of pyqt5-qt5 (5.15.11) could not be found, and the versions available require a different Python version."
  },
  "repository": {
    "name": "AzerothAuctionAssassin",
    "owner": {
      "login": "ff14-advanced-market-search"
    }
  }
}
' http://127.0.0.1:5000/webhook
```

### Running Tests

To run the unit tests, use the following command:

```bash
python -m unittest discover -s tests
```

### Project Structure

```plaintext
GitFailGuard/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── webhook_handler.py
│   ├── log_analyzer.py
│   ├── github_issue_creator.py
├── tests/
│   ├── __init__.py
│   ├── test_webhook_handler.py
│   ├── test_log_analyzer.py
│   ├── test_github_issue_creator.py
├── requirements.txt
├── README.md
├── .env.example
├── setup.py
├── Dockerfile
└── docker-compose.yml
```

## Production Deployment

You can deploy a production app using [the kubeconfig.](https://github.com/cohenaj194/GitFailGuard/blob/main/kube-manifest.yml)

Then follow our guide on [Connecting your github repos to GitFailGuard.](https://github.com/cohenaj194/GitFailGuard/wiki/Setting-Up-a-GitHub-Webhook-for-GitFailGuard)

This application can be deployed using any platform that supports Docker containers, such as Digital Ocean, AWS, Azure, or Google Cloud. Ensure you set the environment variables in the deployment environment as described in the setup section.

### Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [OpenAI](https://www.openai.com/)
- [GitHub Actions](https://github.com/features/actions)

---

If you like what we do support us on [Patreon!](https://www.patreon.com/indopan)

Come join the [Discord](https://discord.gg/836C8wDVNq)

Feel free to reach out if you have any questions or need further assistance.
