
Konfiguracja słuchania strumienia audio z noda ASL3
-------------------------------------------------------

W nowej wersji słuchania strumienia audio z noda ASL3 w ASL-dashboard zostało zastosowane nowe rozwiązanie na bazie MediaMTX (WebRTC). 
Icecast2 używany wczesniej wprowadzał opóźnienie ok. 18–20 sekund. 
Rozwiązanie na bazie MediaMTX (WebRTC) udostępnia audio do słuchania w player na dashboardzie z minimalnym opóźnieniem.

**Ważna uwaga jeśli do tej pory używałeś wysyłanie strumienia audio via Icecast2 musisz wyłączyć 
tę konfigurację:**

Podaj zamiast **123456** numer swojego noda
```
sudo systemctl stop icecast2
sudo systemctl disable icecast2
sudo systemctl stop asl-broadcastify@123456
sudo systemctl disable asl-broadcastify@123456
```

Jeśli chcesz wysyłać strumień audio z swojego noda musimy przekazać dźwięk z Asteriska do utworzonego pliku FIFO. 
Jeśli wcześniej używałeś Icecast2, to pewnie masz ten wpis w rpt.conf, ale możesz się upewnić.
Otwórz plik /etc/asterisk/rpt.conf:

```
sudo nano /etc/asterisk/rpt.conf
```

Znajdź sekcję swojego node'a (np.  ```[63001](node-main)``` i dopisz w niej linię wskazującą na plik FIFO:

Zamiast **XXXXXX** wpisz numer Twojego Noda

    outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/XXXXXX.fifo

Zapisz plik i zrestartuj Asteriska:

```
systemctl restart asterisk
```
-----------------------------------------------

## Instalator (install.sh) wykona następujące elementy:

    Skopiuje pliki niezbędne do katalogu /opt/mediamtx/ w którym będą wszystkie pliki związane z
    uruchomieniem procesu przesyłania audio   

    Pobierze [mediamtx](https://mediamtx.org/) i zainstaluje go w katalogu /opt//mediamtx

    Doda użytkownika do systemu 'mediamtx' (bez możliwości logowania się nim do RPI) dla uruchomienia
    programu mediamtx. Skonfiguruje mediamtx z minimalną konfiguracją.
    
    Otworzy port na RPI 8189/udp aby dashboard mógł odbierać strumień audio

    Sprawdzi, czy w skecji noda w /etc/asterisk/rpt.conf jest dodana linia wysyłania stream audio 
    Jeśli nie ma poda komunikat dla np. podanego numeru noda w install.sh 123456:
       !!  rpt.conf has no outstreamcmd for node 123456. Add to the [123456](node-main) section:
       !!      outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/123456.fifo
       !!  then restart Asterisk. (The installer does not edit rpt.conf.)
    Musisz więc dodać w sekcji swojego noda w rpt.conf linię, w której zamiast 123456 podać swój numer noda:
       outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/60007.fifo
    Następnie wykonać restart asterisk: sudo systemctl restart asterisk

    Uruchomi **asl-mediamtx@.service* dla podanego w parametrze numeru noda aby wysyłał strumień audio z asterisk 
    do mediamtx.

    Skonfiguruje proxy w apache2 które jest niezbędne do całego procesu.

    Następnie ostatni etap to sprawdzenie/uzupełnienienie /var/www/html/confg.ini
    dahboard, który obecnie wymaga swoich  ustawień w sekcji [audio].


## Instlacja

Uruchmom instalator gdzie w parametrze skrytpu podaj numer swój numer noda np 123456

```
sudo -s
cd /opt/asl-utils/mediammtx/
chmod 0755 asl-mediamtx
sudo chmod 0755 install.sh
sudo ./install.sh 123456
```

Kontrola procesów uruchomionych:

Zamiast **123456** podaj numer swojego noda
```
sudo systemctl status asl-mediamtx@123456
sudo systemctl status mediamtx
```

Sprawdź ustawienia w /var/www/html/config.ini szczególnie sekcje [audio]

```
sudo nano /var/www/html/config.ini
```
Zapis edycji użyj klawiszy CTRL+o i następnie CTRL+x

Przykładowy wygląd config.ini gdzie zamiast **SP2ABC** jest Twój znak i zamiast **123456** jest numer Twojego noda

```
[node]
number = 123456
callsign = "SP2ABC"
[security]
internal_networks[] = "127.0.0.1/32"
internal_networks[] = "192.168.1.0/24"
internal_networks[] = "10.0.0.0/8"
internal_networks[] = "172.16.0.0/12"    
; internal_networks[] = "::1/128"           ; localhost IPv6
[audio]
description = "ASL Nod"
webrtc_enabled  = yes ; czy player dostepny na dashboard
webrtc_external = no ; czy player dostepny z poza sieci lokalnej (wymaga otwarcia portu 8189/udp)
; webrtc_path   = 123456   ; opcjonalnie, domyślnie numer noda
```

Poniżej opcje dostępne w skrypcie instalatora:

    install.sh - audio z noda ASL3 w przeglądarce przez WebRTC (MediaMTX)

     sudo ./install.sh NODE [options]
     sudo ./install.sh --uninstall NODE

    Options:
      --replace-broadcastify  disable asl-broadcastify@NODE (it reads the same FIFO)
      --update-config         edit the dashboard config.ini without asking
      --no-config             never touch config.ini
      --config PATH           dashboard config.ini (default /var/www/html/config.ini)

