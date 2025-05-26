import json
import os
import boto3
import logging
from datetime import datetime, timedelta
import urllib3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AWSCostReporter:
    def __init__(self):
        self.ce_client = boto3.client('ce')
        self.http = urllib3.PoolManager()
        self.webhook_url = os.environ['WEBHOOK_URL']
        self.account_name = os.environ.get('ACCOUNT_NAME', 'Unknown')

    def get_dates(self):
        end_date = datetime.utcnow().date()
        return {
            'start_date': (end_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'three_days_ago': (end_date - timedelta(days=3)).strftime('%Y-%m-%d'),
            'first_day_of_month': end_date.replace(day=1).strftime('%Y-%m-%d')
        }

    def get_service_costs(self, start_date, end_date):
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )

            service_costs = []
            total_spend = 0
            other_costs = 0

            for result in response['ResultsByTime'][0]['Groups']:
                service = result['Keys'][0]
                cost = float(result['Metrics']['UnblendedCost']['Amount'])
                if cost <= 0.1:
                    other_costs += cost
                else:
                    service_costs.append((service, cost))
                total_spend += cost

            if other_costs > 0:
                service_costs.append(("Other", other_costs))

            service_costs.sort(key=lambda x: x[1], reverse=True)
            return service_costs, total_spend

        except Exception as e:
            logger.error(f"Error getting service costs: {str(e)}")
            raise

    def get_forecasted_spend(self, start_date, end_date):
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )

            costs = [float(r['Total']['UnblendedCost']['Amount']) for r in response['ResultsByTime']]
            return sum(costs) / len(costs) if costs else 0.0

        except Exception as e:
            logger.error(f"Error getting forecast: {str(e)}")
            raise

    def get_month_spend(self, start_date, end_date):
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={'Start': start_date, 'End': end_date},
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            return float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])

        except Exception as e:
            logger.error(f"Error getting month spend: {str(e)}")
            raise

    def format_message(self, dates, costs):
        service_details = "\n".join([
            f"🔹 {service} – **${cost:.2f}**" for service, cost in costs['service_costs']
        ])

        return (
            f"🔔 **Daily AWS Billing Notification** 🔔\n"
            f"📂 **Project:** {self.account_name}\n\n"
            f"📅 **Yesterday's Spend (UTC - {dates['start_date']}):** **${costs['yesterday_total']:.2f}**\n"
            f"📌 **Service Breakdown:**\n{service_details}\n\n"
            f"📊 **Today's Forecasted Spend (UTC - {dates['end_date']}):** **${costs['forecasted']:.2f}**\n"
            f"🧾 **Total Spend This Month (UTC - {dates['first_day_of_month']} to {dates['end_date']}):** **${costs['month_total']:.2f}**\n"
        )

    def send_to_webex(self, message):
        try:
            headers = {'Content-Type': 'application/json'}
            payload = {'markdown': message}
            encoded_msg = json.dumps(payload).encode('utf-8')

            response = self.http.request('POST', self.webhook_url, body=encoded_msg, headers=headers)

            if response.status == 204:
                return {'statusCode': 204, 'body': 'Message sent successfully to Webex Chat!'}
            return {'statusCode': response.status, 'body': f'Failed to send message to Webex Chat: {response.data}'}

        except Exception as e:
            logger.error(f"Error sending to Webex: {str(e)}")
            raise


def lambda_handler(event, context):
    try:
        reporter = AWSCostReporter()
        dates = reporter.get_dates()

        service_costs, yesterday_total = reporter.get_service_costs(dates['start_date'], dates['end_date'])
        forecasted = reporter.get_forecasted_spend(dates['three_days_ago'], dates['end_date'])
        month_total = reporter.get_month_spend(dates['first_day_of_month'], dates['end_date'])

        costs = {
            'service_costs': service_costs,
            'yesterday_total': round(yesterday_total, 2),
            'forecasted': round(forecasted, 2),
            'month_total': round(month_total, 2)
        }

        message = reporter.format_message(dates, costs)
        return reporter.send_to_webex(message)

    except Exception as e:
        logger.error(f"Error in lambda handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Internal server error: {str(e)}'
        }
