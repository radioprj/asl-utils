# System alertów meteorologicznych dla AllStarLink

Zestaw skryptów oraz plików dźwiękowych służący do generowania i odczytywania alertów meteorologicznych dla wskazanego obszaru.

Alerty obejmują informacje o zagrożeniach oraz ich stopniu, między innymi dotyczące:

- opadów deszczu,
- opadów śniegu,
- temperatury,
- silnego wiatru,
- burz,
- trąb powietrznych.

System bazuje na danych udostępnianych przez serwis:

https://burze.dzis.net

Przed rozpoczęciem korzystania z usługi zaleca się zapoznanie z zasadami serwisu:

https://burze.dzis.net/?page=zasady

Dodatkowo, jeśli w monitorowanym obszarze występują burze, system może podawać informacje o:

- kierunku przemieszczania się burzy,
- liczbie wyładowań atmosferycznych,
- odległości burzy od wskazanej lokalizacji.

## Konfiguracja API

Aby korzystać z danych udostępnianych przez serwis, należy założyć konto i wygenerować własny klucz API.

Klucz API można uzyskać po zalogowaniu się do serwisu, wybierając pozycję **API** z menu użytkownika.

Aktualny limit wynosi **10 zapytań na minutę**.

## Instalacja

Zainstaluj wymagane biblioteki:

```bash
sudo -s
/opt/asl-utils/meteo-alerts/install-pkg.sh
```
Konfiguracja

Klucz API z serwisu burze.dzis.net należy wpisać w pliku alerts.ini, zastępując przykładową wartość:
```
key=12345678901234567890
```

W tym samym pliku należy podać:

współrzędne geograficzne punktu centralnego (lat, lon),
promień monitorowanego obszaru w kilometrach (range_detect).

Na podstawie tych parametrów będą pobierane alerty dla wybranego regionu.

Konfiguracja CRON

Plik alerts-cron należy skopiować do katalogu /etc/cron.d/:
```
sudo -s
cp /opt/asl-utils/meteo-alerts/alerts-cron /etc/cron.d/
chown root:root /etc/cron.d/alerts-cron
```

Jeżeli dla wskazanego obszaru będą dostępne ostrzeżenia meteorologiczne, system będzie je automatycznie odtwarzał:

o pełnej godzinie,
30 minut po każdej pełnej godzinie będą dodatkowo odtwarzane informacje o aktywnych burzach.

Szczegóły harmonogramu znajdują się w katalogu:
```
/opt/asl-utils/scripts
```
**Dostęp przez DTMF**

Możesz dodać kod DTMF *620, który umożliwi ręczne odtworzenie aktualnych alertów meteorologicznych.

Zrób edycje pliku:
```
sudo nano /opt/asl-utils/meteo-alerts/play-alerts.sh
```
Wpisz numer swojego noda w **NODE=**  i zapisz plik

Następnie skopiuj ten plik do katalogu /etc/asterisk/scripts/
```
sudo cp /opt/alsa-utils/meteo-alerts/play-alerts.sh /etc/asterisk/scripts/
sudo chown asterisk:asterisk /etc/asterisk/scripts/play-alerts.sh
```

Zrób edycje pliku:
```
sudo nano /etc/asterisk/rpt.conf
```

w sekcji [functions-main] odszukaj fragment:
```
;;;;; Autopatch Commands ;;;;;
; Note, This may be a good place for other 2 digit frequently used commands
;61 = autopatchup,noct = 1,farenddisconnect = 1,dialtime = 20000
;62 = autopatchdn
```

i dopisz:
```
; Meteo Alerts
620=cmd,/etc/asterisk/scripts/play-alerts.sh
```

Po zapisaniu zmian uruchom ponownie usługę Asterisk:
```
sudo systemctl restart asterisk
```
Integracja z ASL-Dashboard

Jeżeli korzystasz z projektu:

https://github.com/radioprj/ASL-Dashboard

możesz dodać przycisk wywołujący odczyt aktualnych alertów meteorologicznych.

W pliku:

/var/www/html/buttons.ini


dodaj za sekcją [parrot_off]:
```ini
[meteo-alerts]
title = Meteo Alerts
color = blue
cmds[] = *620
```

Po zapisaniu zmian w panelu pojawi się niebieski przycisk umożliwiający odtworzenie aktualnych alertów.

Uwagi końcowe

Należy mieć świadomość, że rozwiązanie zostało napisane w języku Python i korzysta z zewnętrznych bibliotek.

Python jest bardzo elastycznym i wygodnym językiem programowania, jednak aplikacje korzystające z zewnętrznych modułów mogą być podatne na zmiany wprowadzane przez autorów tych bibliotek. W niektórych przypadkach aktualizacja modułów może wymagać dostosowania kodu skryptów.

Nie jest to częste zjawisko, jednak warto mieć świadomość, że może wystąpić.

Autor nie zapewnia wsparcia technicznego ani bieżącego utrzymania opisanych skryptów. Decydując się na ich używanie, akceptujesz ten fakt i w przypadku problemów będziesz musiał samodzielnie poszukać rozwiązania, korzystając z dokumentacji oraz zasobów dostępnych w Internecie.


