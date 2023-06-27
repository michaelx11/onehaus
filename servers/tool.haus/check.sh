#!/bin/bash

set -e

# Helper function to check if a process with substring is running
check_process() {
    process=`ps -ef | grep $1 | grep -v grep | wc -l`
    if [ $process -eq 0 ]; then
        # Red colored error
        printf "\033[0;31m$1 is not running\033[0m\n"
    else
        echo "$1 is running"
    fi
}

# Check mysql, nginx, fail2ban
check_process "nginx"
check_process "fail2ban"

# Check nginx virtual hosts
NGINX_T_OUTPUT=`nginx -T`
# Check for individual virtual hosts by domain
LIST_OF_DOMAINS=("mx.store.haus")
for domain in "${LIST_OF_DOMAINS[@]}"
do
    if [[ $NGINX_T_OUTPUT == *"$domain"* ]]; then
        echo "$domain is configured"
    else
        printf "\033[0;31m$domain is not configured\033[0m\n"
    fi
done

# Check that fail2ban is configured
FAIL2BAN_STATUS=`fail2ban-client status`
if [[ $FAIL2BAN_STATUS == *"Jail list"* ]]; then
    echo "Fail2ban is configured"
else
    printf "\033[0;31mFail2ban is not configured\033[0m\n"
fi

# Check certbot is configured
CERTBOT_STATUS=`certbot certificates`
if [[ $CERTBOT_STATUS == *"Found the following certs"* ]]; then
    echo "Certbot is configured"
    # Check all the domains in LIST_OF_DOMAINS are in the certbot certificates
    for domain in "${LIST_OF_DOMAINS[@]}"
    do
        if [[ $CERTBOT_STATUS == *"$domain"* ]]; then
            echo "$domain is configured"
        else
            printf "\033[0;31m$domain is not configured\033[0m\n"
        fi
    done
else
    printf "\033[0;31mCertbot is not configured\033[0m\n"
fi

# Check for "nodejs app.js" running as user "web"
NODEJS_PROCESS=`ps -ef | grep "nodejs app.js" | grep -v grep | grep -v root | grep web | wc -l`
if [ $NODEJS_PROCESS -eq 0 ]; then
    # Red colored error
    printf "\033[0;31mnodejs app.js is not running\033[0m\n"
    # To remediate, cd to /home/web/micro-filecache/node, start a tmux session and run "sudo -u web nodejs app.js"
    printf "\033[0;31mTo remediate, cd to /home/web/micro-filecache/node, start a tmux session and run \"sudo -u web nodejs app.js\"\033[0m\n"
else
    echo "nodejs app.js is running as web"
fi
