# GitFailGuard

GitFailGuard is an AI-powered tool that automatically reviews failed GitHub Actions and creates detailed GitHub Issues to help you quickly address problems.

## Features

- Automated detection of failed GitHub Actions.
- AI-powered log analysis to identify potential causes of failure.
- Automatic creation of GitHub Issues with detailed failure information.

## Setup

### Prerequisites

- Docker
- Docker Compose
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

You can test the webhook endpoint using `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "action": "completed",
  "workflow_run": {
    "conclusion": "failure",
    "name": "Test Workflow",
    "logs_url": "https://github.com/ff14-advanced-market-search/mysql-population/actions/runs/9199994409"
  },
  "repository": {
    "full_name": "ff14-advanced-market-search/mysql-population"
  }
}' http://localhost:5000/webhook
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

### Deployment

This application can be deployed using any platform that supports Docker containers, such as AWS, Azure, or Google Cloud. Ensure you set the environment variables in the deployment environment as described in the setup section.

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