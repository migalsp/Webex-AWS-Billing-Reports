# AWS Cost Reporter for Webex

[![CI/CD](https://github.com/migalsp/Webex-AWS-Billing-Reports/actions/workflows/ci.yml/badge.svg)](https://github.com/migalsp/Webex-AWS-Billing-Reports/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/migalsp/Webex-AWS-Billing-Reports/branch/main/graph/badge.svg)](https://codecov.io/gh/migalsp/Webex-AWS-Billing-Reports)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

> AWS Lambda function that automatically reports daily AWS costs to Webex spaces via webhooks.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/migalsp/Webex-AWS-Billing-Reports.git
cd Webex-AWS-Billing-Reports

# Install dependencies
pip install -r build/requirements/requirements.txt

# Deploy (after downloading the release)
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name cost-reporter \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    WebexWebhookUrl=YOUR_WEBEX_WEBHOOK_URL \
    AccountName=YOUR_ACCOUNT_NAME
```

## Features

- 📊 Daily cost reporting via Webex notifications
- 🔍 Detailed service-level cost breakdown
- 📈 Cost forecasting for the current day
- 📅 Monthly cost tracking

## Prerequisites

- AWS Account with Cost Explorer enabled
- Webex space with webhook URL
- AWS CLI configured with appropriate permissions
- Python 3.13+

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `WebexWebhookUrl` | Webex webhook URL | - |
| `AccountName` | AWS account name | Unknown |
| `ScheduleExpression` | CloudWatch schedule | `cron(0 0 * * ? *)` |
| `LambdaMemorySize` | Memory size (MB) | 128 |
| `LambdaTimeout` | Timeout (seconds) | 60 |

## Project Structure

```text

.
├── .github/          # GitHub Actions workflows
├── build/           # Build artifacts and dependencies
├── src/             # Source code
│   └── lambda/     # Lambda function
├── templates/       # CloudFormation templates
└── tests/          # Unit tests
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

- IAM role with least privilege permissions
- Secure parameter storage
- Pinned dependencies
- Regular security updates

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📝 [Open an issue](https://github.com/migalsp/Webex-AWS-Billing-Reports/issues)
- 💬 [Discussions](https://github.com/migalsp/Webex-AWS-Billing-Reports/discussions)
