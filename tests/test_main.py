from main import AWSCostReporter, lambda_handler
import os

# Environment variable stubs for tests
os.environ["WEBHOOK_URL"] = "https://example.com/webhook"
os.environ["ACCOUNT_NAME"] = "TestAccount"


def test_get_dates():
    reporter = AWSCostReporter()
    dates = reporter.get_dates()
    assert "start_date" in dates
    assert "end_date" in dates
    assert "three_days_ago" in dates
    assert "first_day_of_month" in dates


def test_format_message():
    reporter = AWSCostReporter()
    dates = {
        "start_date": "2024-07-01",
        "end_date": "2024-07-02",
        "three_days_ago": "2024-06-29",
        "first_day_of_month": "2024-07-01",
    }
    costs = {
        "service_costs": [("EC2", 10.0), ("S3", 2.5)],
        "yesterday_total": 12.5,
        "forecasted": 15.0,
        "month_total": 100.0,
    }
    message = reporter.format_message(dates, costs)
    assert "AWS Billing Notification" in message
    assert "$12.50" in message
    assert "EC2" in message
    assert "S3" in message


def test_lambda_handler_error(monkeypatch):
    # Check that lambda_handler returns 500 on error
    def broken_init(self):
        raise Exception("fail")

    monkeypatch.setattr(AWSCostReporter, "__init__", broken_init)
    result = lambda_handler({}, {})
    assert result["statusCode"] == 500
    assert "Internal server error" in result["body"]
