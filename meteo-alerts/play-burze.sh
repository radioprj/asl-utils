#!/bin/bash
#
# Wpisz numer swojego noda zamiast 123456
NODE="123456"

# odtwrazanie meteo alert jeśli plik istnieje
if [ -f "/opt/asl-utils/meteo-alerts/status/burza.ulaw" ]; then
  /usr/sbin/asterisk -rx "rpt localplay $NODE /opt/asl-utils/meteo-alerts/status/burza"
fi
