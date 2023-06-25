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
check_process "mysql"
check_process "nginx"
check_process "fail2ban"

# Check nginx virtual hosts
NGINX_T_OUTPUT=`nginx -T`
# Check for individual virtual hosts by domain
LIST_OF_DOMAINS=("swarm.link" "ware.haus" "reinforce.dev" "db.ware.haus" "u2f.ware.haus")
for domain in "${LIST_OF_DOMAINS[@]}"
do
    if [[ $NGINX_T_OUTPUT == *"$domain"* ]]; then
        echo "$domain is configured"
    else
        printf "\033[0;31m$domain is not configured\033[0m\n"
    fi
done

# Check that mysql is insecure with authentication by trying to login
MYSQL_LOGIN=`mysql -u root -e "SHOW DATABASES;" 2>&1`
if [[ $MYSQL_LOGIN == *"Access denied"* ]]; then
    echo "MySQL is secure"
else
    printf "\033[0;31mMySQL is insecure\033[0m\n"
fi

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

# Check that django is running on port 7865
DJANGO_PORT=`netstat -tulpn | grep 7865`
if [[ $DJANGO_PORT == *"python"* ]]; then
    echo "Django is running"
else
    printf "\033[0;31mDjango is not running\033[0m\n"
fi
