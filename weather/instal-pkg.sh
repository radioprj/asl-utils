#!/bin/bash

echo ""
echo "Instalacja bibliotek "
echo ""

apt-get update
apt-get -y install sox libsox-dev curl python3 python3-dev python3-numpy python3-pip python3-requests
python3 -m pip install sox --break-system-packages

echo ""
echo "Biblioteki zainstalowane"
echo ""
