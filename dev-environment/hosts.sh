#!/bin/bash

HOSTS_FILE="/hosts"

function addhost() {
  HOSTNAME="$1"
  ADDRESS="$2"
  LINE="$ADDRESS    $HOSTNAME"
  echo "grep $LINE $HOSTS_FILE"
  if ! grep $HOSTNAME $HOSTS_FILE; then
    echo "Adding host"
    echo "$LINE" >> $HOSTS_FILE
  fi
}

#function removehost() {
#  HOSTNAME="$1"
#  if grep $HOSTNAME $HOSTS_FILE; then
#    echo "Removing host"
#    sed -i".bak" "/$HOSTNAME/d" $HOSTS_FILE
#  fi
#}

# trap 'removehost "selvbetjening-web"' EXIT
trap 'exit' EXIT

addhost "selvbetjening-web selvbetjening-test-idp" "127.0.0.1"

sleep infinity & wait $!
