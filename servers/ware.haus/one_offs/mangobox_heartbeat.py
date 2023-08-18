import re
import subprocess
import time
from datetime import datetime, timedelta

# Updated regular expression pattern
LOG_PATTERN = r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<date>.*?):(?P<time>.*?) \+0000\] "GET /mangobox_heartbeat HTTP/1.1"'

# Convert nginx log date-time format to a Python datetime object
def parse_nginx_datetime(date_str, time_str):
    return datetime.strptime(date_str + " " + time_str, "%d/%b/%Y %H:%M:%S")

def alert(msg):
    # TODO: replace this with a twilio text or something else
    print("mango heartbeat: " + msg)
    subprocess.call(["curl", "-X", "POST", "https://api.twilio.com/2010-04-01/Accounts/[account]/Messages.json", "--data-urlencode", "Body=" + msg, "--data-urlencode", "From=+12678002018", "--data-urlencode", "To=+14242105075", "-u", "[account]:[token]"])

def scan_log():
    last_time = None
    last_alert_time = None

    with open("/var/log/nginx/access.log", "r") as f:
        for line in f:
            match = re.search(LOG_PATTERN, line)
            if match:
                current_ip = match.group('ip')
                current_time = parse_nginx_datetime(match.group('date'), match.group('time'))
                now = datetime.now()

                if current_ip != "75.223.210.70":
                    if last_alert_time:
                        delta = now - last_alert_time
                        if delta > timedelta(minutes=30):
                            alert("IP has switched from Verizon: %s" % current_ip)
                            last_alert_time = now
                            continue

                if last_time:
                    delta = current_time - last_time
                    if delta > timedelta(minutes=2):
                        if last_alert_time:
                            delta = now - last_alert_time
                            if delta > timedelta(minutes=30):
                                alert("Two minutes since last heartbeat")
                                last_alert_time = now

                last_time = current_time
    print("mango heartbeat %s: scan complete: ip: %s, time: %s" % (datetime.now(), current_ip, current_time))

if __name__ == "__main__":
    # Scan every 30 seconds
    while True:
        scan_log()
        time.sleep(30)
