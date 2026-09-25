#!/bin/bash
# skrytp wykonywany o pełnych godzinach

# Wpisz numer swojego noda
NODE="124567"

# skrypt ktory o pełnej godzinie mówi czas
if [ -f "/usr/bin/asl-saypl" ];  then
/usr/bin/asl-saypl -n ${NODE} -w time24
fi
# Nastepnie jesli jest status pogody to podaje pogode
# Pobierz aktualną godzinę w formacie 00-23 (bez wiodącego zera, np. 8, 12, 16, 20)
CURRENT_HOUR=$(date +%-H)
# Sprawdź, czy aktualna godzina jest na liście (8, 12, 16, 20)
case "$CURRENT_HOUR" in
    8|12|16|20)
  /opt/asl-utils/weather/play-wx.sh
esac

# Na koniec zawsze jesli sa dostepne alerty
/opt/asl-utils/meteo-alerts/play-alerts.sh
