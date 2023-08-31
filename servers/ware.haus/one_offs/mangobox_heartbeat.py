import re
import subprocess
import time
from datetime import datetime, timedelta

# Updated regular expression pattern
LOG_PATTERN = r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(?P<date>.*?):(?P<time>.*?) \+0000\] "GET /mangobox_heartbeat HTTP/1.1"'


# Convert nginx log date-time format to a Python datetime object
def parse_nginx_datetime(date_str, time_str):
    return datetime.strptime(date_str + " " + time_str, "%d/%b/%Y %H:%M:%S")


def turn_off_gateway():
    """curl -X POST -H "Content-Type: application/json" -d '{}' http://maker.ifttt.com/trigger/turn_off_kasa/json/with/key/d3NWez5fqnOqRIkPVs8X9Y"""
    print("mango heartbeat: turning off gateway")
    # Use subprocess.call instead of requests.post to limit dependencies
    subprocess.call(
        [
            "curl",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            "-d",
            "{}",
            "http://maker.ifttt.com/trigger/turn_off_kasa/json/with/key/d3NWez5fqnOqRIkPVs8X9Y",
        ]
    )


def turn_on_gateway():
    """curl -X POST -H "Content-Type: application/json" -d '{}' http://maker.ifttt.com/trigger/turn_on_kasa/json/with/key/d3NWez5fqnOqRIkPVs8X9Y"""
    print("mango heartbeat: turning on gateway")
    subprocess.call(
        [
            "curl",
            "-X",
            "POST",
            "-H",
            "Content-Type: application/json",
            "-d",
            "{}",
            "http://maker.ifttt.com/trigger/turn_on_kasa/json/with/key/d3NWez5fqnOqRIkPVs8X9Y",
        ]
    )


def alert(msg):
    # TODO: replace this with a twilio text or something else
    print("mango heartbeat: " + msg)
    subprocess.call(
        [
            "curl",
            "-X",
            "POST",
            "https://api.twilio.com/2010-04-01/Accounts/[account]/Messages.json",
            "--data-urlencode",
            "Body=" + msg,
            "--data-urlencode",
            "From=+12678002018",
            "--data-urlencode",
            "To=+14242105075",
            "-u",
            "account:token",
        ]
    )


def time_between_alerts():
    """Based on time of day, return how long to wait between alerts

    if it's 9am-11pm in Los Angeles, then alert every 15 minutes
    otherwise, alert every 6 hours to allow for sleep
    """
    # Make sure to use Los Angeles time by taking utctime and subtracting 7 hours
    now = datetime.utcnow() - timedelta(hours=7)
    if now.hour >= 9 and now.hour <= 23:
        return timedelta(minutes=15)
    else:
        return timedelta(hours=6)


last_alert_time = datetime.now() - timedelta(minutes=100000)


def scan_log():
    global last_alert_time
    last_time = None
    current_ip = None
    current_time = None
    non_verizon_ips = 0
    filtered_lines = []  # Store the last filtered lines
    total_lines = 0

    with open("/var/log/nginx/access.log", "r") as f:
        for line in f:
            total_lines += 1
            match = re.search(LOG_PATTERN, line)
            if match:
                filtered_lines.append(line)
                if len(filtered_lines) > 2:  # Keep only the last 2 filtered lines
                    filtered_lines.pop(0)

        now = datetime.now()
    # Process the last two filtered lines
    for line in filtered_lines:
        match = re.search(LOG_PATTERN, line)
        if match:
            current_ip = match.group("ip")
            parsed_time = parse_nginx_datetime(match.group("date"), match.group("time"))

            # Check that it's equal to the spectrum IP, which seems more consistent
            if current_ip.startswith("172.91.73."):
                non_verizon_ips += 1
            else:
                non_verizon_ips = 0

            last_time = parsed_time

    if non_verizon_ips >= 2:
        if last_alert_time:
            delta = now - last_alert_time
            if delta > time_between_alerts():
                alert("ip has switched: %s" % current_ip)
                # Turn off gateway, wait 30 seconds, then turn it back on
                turn_off_gateway()
                time.sleep(30)
                turn_on_gateway()
                alert("gateway turned off and on")
                last_alert_time = now

    if not last_time:
        # If we never got a log line, then consider it to be at least an hour long
        print("could not find a log line")
        last_time = datetime.now() - timedelta(hours=1)
    current_time = datetime.now()
    delta = current_time - last_time
    if delta > timedelta(minutes=5):
        if last_alert_time:
            delta = now - last_alert_time
            if delta > time_between_alerts():
                # Check that the log wasn't just rotated
                if total_lines > 10:
                    alert("Five minutes since last heartbeat")
                    last_alert_time = now

    print(
        "mango heartbeat %s: scan complete: ip: %s, time: %s"
        % (datetime.now(), current_ip, last_time)
    )


if __name__ == "__main__":
    # Scan every 30 seconds
    while True:
        scan_log()
        time.sleep(30)
