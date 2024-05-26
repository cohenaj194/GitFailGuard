# GitFailGuard

<p align="center">
  <img src="https://github.com/cohenaj194/GitFailGuard/assets/17516896/ab1733a6-dff9-46aa-a909-2ac27f18ad0d" width="200">
</p>

<!-- ![GitFailGuard](https://github.com/cohenaj194/GitFailGuard/assets/17516896/ab1733a6-dff9-46aa-a909-2ac27f18ad0d) -->

**GitFailGuard** is an advanced AI-powered tool designed to streamline your development workflow by automatically reviewing failed GitHub Actions and generating detailed GitHub Issues. This enables you to quickly identify and address problems, ensuring a more efficient development process.

Key Features:
- **CI/CD Failure Analysis**: GitFailGuard reviews failed GitHub Actions and creates comprehensive GitHub Issues, providing clear insights and actionable steps to resolve issues.
- **Github Issue Question Assistant**: Mention `@GitFailGuard` in any GitHub issue comment, and GitFailGuard will respond to your questions, offering assistance and guidance directly within your repository.
- **CI/CD Log Analysis in Pull Requests**: GitFailGuard can post logs from failed actions directly into your pull requests, facilitating thorough reviews from [CodeRabbit](https://coderabbit.ai/) with `@coderabbitai` pings and ensuring code quality.

With GitFailGuard, you can enhance your CI/CD pipeline, improve code review processes, and maintain high standards of code quality effortlessly.

[Sequence-Diagram](https://github.com/cohenaj194/GitFailGuard/wiki/Sequence-Diagram)

## Features

- Automated detection of failed GitHub Actions.
- AI-powered log analysis to identify potential causes of failure.
- Automatic creation of GitHub Issues with detailed failure information.
- Assistant feature to respond to questions in GitHub issue comments when mentioned with `@GitFailGuard`.
- Interaction with [CodeRabbit](https://coderabbit.ai/) with `@coderabbitai` pings to enable log reviews inside of pull requests.

### Example

- [Issue Example](https://github.com/ff14-advanced-market-search/saddlebag-with-pockets/issues/431)
- [Comment Example](https://github.com/cohenaj194/GitFailGuard/issues/6#issuecomment-2131357637)
- [CodeRabbit Review Ping](https://github.com/ff14-advanced-market-search/AzerothAuctionAssassin/issues/97) and [resulting comment](https://github.com/ff14-advanced-market-search/AzerothAuctionAssassin/pull/94#issuecomment-2132261750)

## Setup

### Prerequisites

- Docker and Docker Compose
- GitHub token with appropriate permissions
- OpenAI API key

### Environment Variables

Ensure you have the following environment variables set:

- `GITHUB_TOKEN`: Your GitHub token.
- `OPENAI_API_KEY`: Your OpenAI API key.
- `ENABLE_CODERABBIT`: (Optional) Enables CodeRabbit reviews in pull requests.

You can set these variables in your shell:

```bash
export GITHUB_TOKEN=your_github_token_here
export OPENAI_API_KEY=your_openai_api_key_here

# # only set if you want to enable coderabit PR comments to failure logs
# # do not set env var if you do not have coderabit enabled
# export ENABLE_CODERABBIT="true"
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
