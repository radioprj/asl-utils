# Aktualny stan pogody z OpenWeatherMap dla AllStarLink

Zestaw skryptów oraz plików dźwiękowych służący do generowania i odczytywania aktualnych informacji pogodowych dla wskazanej lokalizacji.

Dostępne informacje:

- temperatura
- wilgotność
- ciśnienie atmosferyczne
- prędkość i kierunek wiatru
- zachmurzenie
- informacje o opadach (jeżeli są dostępne)

System bazuje na danych udostępnianych przez serwis:

https://openweathermap.org

Aby korzystać z usługi, należy założyć konto w serwisie OpenWeatherMap i wygenerować własny klucz API umożliwiający pobieranie danych pogodowych.

## Instalacja

Zainstaluj wymagane biblioteki:

```bash
sudo -s
/opt/asl-utils/weather/install-pkg.sh
```

Konfiguracja klucza API

Klucz API uzyskany z serwisu OpenWeatherMap należy wpisać w pliku wxopwm.ini, zastępując wartość przykładową:
```
key=12345678901234567890
```

W tym samym pliku należy również podać współrzędne geograficzne lokalizacji (lat, lon), dla której mają być pobierane dane pogodowe.

Konfiguracja CRON

Plik wx-cron należy skopiować do katalogu /etc/cron.d/:
```
sudo -s
cp /opt/asl-utils/weather/wx-cron /etc/cron.d/
chown root:root /etc/cron.d/wx-cron
```

W wybranych godzinach (domyślnie: 08:00, 12:00, 16:00 oraz 20:00) system będzie odtwarzał aktualny komunikat pogodowy.

Szczegóły konfiguracji znajdują się w katalogu:

/opt/asl-utils/scripts

Dostęp przez DTMF

Możesz dodać kod DTMF *610, który umożliwi odczyt aktualnej pogody z poziomu AllStarLink.

W tym celu w pliku:

/etc/asterisk/rpt.conf


w sekcji [functions-main] odszukaj fragment:

;;;;; Autopatch Commands ;;;;;
; Note, This may be a good place for other 2 digit frequently used commands
;61 = autopatchup,noct = 1,farenddisconnect = 1,dialtime = 20000
;62 = autopatchdn


i dopisz poniższą linię:

; Pogoda OpenWeatherMap
610=cmd,/etc/asterisk/scripts/play-wx.sh


Po zapisaniu zmian uruchom ponownie usługę Asterisk:

sudo systemctl restart asterisk

Integracja z ASL-Dashboard

Jeżeli korzystasz z projektu:

http://github.com/radioprj/ASL-Dashboard

możesz dodać przycisk wywołujący odczyt aktualnej pogody.

W pliku:

/var/www/html/buttons.ini


dodaj poniższą sekcję za wpisem [parrot_off]:
```ini
[weather]
title = Weather
color = blue
cmds[] = *610
```

Po zapisaniu zmian na pulpicie pojawi się niebieski przycisk wywołujący komunikat pogodowy.

Uwagi końcowe

Należy mieć świadomość, że rozwiązanie zostało napisane w języku Python i korzysta z zewnętrznych bibliotek.

Python jest bardzo elastycznym i wygodnym językiem programowania, jednak aplikacje napisane z jego wykorzystaniem mogą być wrażliwe na zmiany w bibliotekach lub modułach zewnętrznych. Autorzy tych komponentów mogą w przyszłości wprowadzać zmiany wymagające dostosowania kodu skryptów.

Nie jest to częsta sytuacja, jednak warto mieć świadomość, że może wystąpić.

Autor nie zapewnia wsparcia technicznego ani bieżącego utrzymania opisywanych skryptów. Decydując się na ich używanie, akceptujesz ten fakt i w przypadku problemów będziesz musiał samodzielnie poszukać rozwiązania, korzystając z dostępnej dokumentacji oraz zasobów Internetu.


