#!/bin/bash
#
# Wpisz swój node numer zamiast 123456
NODE="123456"

# play meteo alert jeśli plik istnieje
if [ -f "/opt/asl-utils/meteo-alerts/status/meteo.ulaw" ];  then
  /usr/sbin/asterisk -rx "rpt localplay ${NODE} /opt/asl-utils/meteo-alerts/status/meteo"
fi
