import requests
import ssl
import socket
import datetime
import os

def get_ssl_expiry(domain):
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()
            expire_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            remaining_days = (expire_date - datetime.datetime.now()).days
            return remaining_days

def send_slack_alert(webhook_url, domain, remaining_days):
    message = (
        "SSL Expiry Alert \n"
        " *Domain: {}\n"
        " *Warning: The SSL certificate for {} will expire in {} days."
    ).format(domain, domain, remaining_days)

    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    if response.status_code == 200:
        print("Alert sent for {}".format(domain))
    else:
        print("Failed to send alert for {}".format(domain))

if __name__ == "__main__":
    DOMAINS_FILE = "domains.txt"

    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, "r") as file:
            domains = file.read().splitlines()
    else:
        print("{} not found!".format(DOMAINS_FILE))
        exit(1)

    SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL environment variable not set.")
        exit(1)

    for domain in domains:
        if len(domain) > 1:
            remaining_days = get_ssl_expiry(domain)
            print("Domain: {}".format(domain))
            print("Remaining days: {}".format(remaining_days))

            send_slack_alert(SLACK_WEBHOOK_URL, domain, remaining_days)

            
