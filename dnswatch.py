import dns.resolver
import time
import smtplib
from email.message import EmailMessage
import threading

# Configuration
dns_servers = ["8.8.8.8", "8.8.4.4"]
domain_to_query = "example.com"
alert_email = "your_email@example.com"
email_server = "smtp.example.com"
email_login = "your_login"
email_password = "your_password"
normal_interval = 300  # 5 minutes in seconds
fast_interval = 60  # 1 minute in seconds
threshold_time = 0.5  # in seconds

def query_dns(server, domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    try:
        start_time = time.time()
        answers = resolver.resolve(domain)
        response_time = time.time() - start_time
        return response_time, answers.rrset.items
    except Exception as e:
        return None, str(e)

def send_alert(message):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = 'DNS Server Alert'
    msg['From'] = alert_email
    msg['To'] = alert_email
    s = smtplib.SMTP(email_server)
    s.starttls()
    s.login(email_login, email_password)
    s.send_message(msg)
    s.quit()
    print("Alert sent:", message)

def monitor_dns():
    while True:
        results = []
        for server in dns_servers:
            response_time, response = query_dns(server, domain_to_query)
            results.append((response_time, response))
        
        if results[0][0] is None or results[1][0] is None:
            send_alert(f"One of the DNS servers failed to respond. Errors: {results[0][1]}, {results[1][1]}")
            current_interval = fast_interval
        elif abs(results[0][0] - results[1][0]) > threshold_time or results[0][1] != results[1][1]:
            send_alert("DNS response discrepancy detected")
            current_interval = fast_interval
        else:
            current_interval = normal_interval
        
        print(f"Next check in {current_interval} seconds.")
        time.sleep(current_interval)

if __name__ == "__main__":
    monitor_thread = threading.Thread(target=monitor_dns)
    monitor_thread.start()
