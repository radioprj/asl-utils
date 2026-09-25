#!/bin/bash
# odtwrazanie meteo alert jeśli plik istnieje

# Wpisz swój numer noda zamiast 123456
NODE="123456"

if [ -f "/opt/asl-utils/weather/status/wx.ulaw" ];  then
  /usr/sbin/asterisk -rx "rpt localplay $NODE /opt/asl-utils/weather/status/wx"
fi
