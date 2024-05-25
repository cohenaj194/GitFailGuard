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

## Local Testing

[View our guide on how to test GitFailGuard locally for developers looking to contribute and fork this project.](https://github.com/cohenaj194/GitFailGuard/wiki/Local-Development-Testing-Guide)

## Production Deployment

You can deploy a production app using docker-compose or [kubernetes.](https://github.com/cohenaj194/GitFailGuard/blob/main/kube-manifest.yml)

Then follow our guide on [Connecting your github repos to GitFailGuard.](https://github.com/cohenaj194/GitFailGuard/wiki/Setting-Up-a-GitHub-Webhook-for-GitFailGuard)

This application can be deployed using any platform that supports Docker containers, such as Digital Ocean, AWS, Azure, or Google Cloud. Ensure you set the environment variables in the deployment environment as described in the setup section.

## Other Notes

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

### Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### License

This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for more details.

### Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [OpenAI](https://www.openai.com/)
- [GitHub Actions](https://github.com/features/actions)

---

If you like what we do support us on [Patreon!](https://www.patreon.com/indopan)

Come join the [Discord](https://discord.gg/836C8wDVNq)

Feel free to reach out if you have any questions or need further assistance.
