# Różne skrypty używane w asl-utils

## hourly_announce.sh

Skrypt służący do automatycznego odtwarzania komunikatów głosowych:

- aktualnego czasu o pełnych godzinach,
- aktualnej pogody z OpenWeatherMap o godzinach 08:00, 12:00, 16:00 oraz 20:00,
- alertów meteorologicznych z serwisu burze.dzis.net o pełnych godzinach (jeżeli są dostępne),
- informacji o aktywnych burzach co 30 minut (jeżeli występują w monitorowanym obszarze).

## Instalacja

Skopiuj plik CRON do katalogu `/etc/cron.d`:

```bash
sudo -s
cp play-cron /etc/cron.d/
chown root:root /etc/cron.d/play-cron

Konfiguracja
Pogoda OpenWeatherMap

Szczegóły konfiguracji znajdują się w katalogu:

/opt/asl-utils/weather/

Alerty meteorologiczne

Szczegóły konfiguracji znajdują się w katalogu:

/opt/asl-utils/meteo-alerts/

**Wymagania**

Wymagana jest instalacja:

polskich plików dźwiękowych:
```
https://github.com/radioprj/ASL-sound-pl
``
- polskiej wersji skryptu asl-say:

```
/opt/asl-utils/asl-say/
```


