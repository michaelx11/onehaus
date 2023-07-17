#!/bin/bash

# Given a list of urls, run curl on each url and print the status code with color coding

# URLS include the protocol, "https://streetparkingmap.com"
URLS=(
"https://streetparkingmap.com"
'https://streetparkingmap.com/get_readable_signs/?minlat=34.02506963967363&minlng=-118.45010683408103&maxlat=34.033676642003336&maxlng=-118.43840167394004'
'https://gachaguide.com'
'https://vaporwarecheck.com'
'https://app.proxychat.xyz'
'https://api.proxychat.xyz/swagger/index.html'
'https://mx.store.haus'
'https://tools.ack.dev'
'https://ack.dev'
'https://autoideate.com'
'https://util.in'
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

for url in "${URLS[@]}"
do
  status_code=$(curl -s -o /dev/null --max-time 5 -w "%{http_code}" $url)
  if [ $status_code -eq 200 ]; then
    echo -e "${GREEN}$status_code${NC} $url"
  else
    echo -e "${RED}$status_code${NC} $url"
  fi
done
