Konfiguracja serwera Icecast do wysyłania strumienia audio w lokalnej sieci domowej
---------------------------------------------------

Poniżej opis, jak uruchomić na swoim nodzie ASL wysyłanie strumienia audio w lokalnej sieci
i słuchać go w np. ASL Dashboard. **Pamiętaj, że audio odbierane via strumień Icecast
idzie z opóźnieniem (od kilku do kilkunastu sekund) do realnego audio i służy tylko do monitorowania aktywności na nodzie**.
Wynika to z tego, że Chrome, Firefox itp. domyślnie buforują od kilku do kilkunastu sekund danych, zanim w ogóle zaczną odtwarzać dźwięk, aby zapobiec przerwom w razie wahań sieci.

Zaloguj się na swój węzeł przez SSH i przejdź na konto administratora:

```
sudo -s
```

Krok 1: Instalacja serwera Icecast

Zaktualizuj listę pakietów i zainstaluj serwer icecast2:
```
apt update
apt install icecast2 -y
```

Podczas instalacji pojawi się tekstowy kreator konfiguracji:
System zapyta, czy chcesz skonfigurować Icecast2 – wybierz Tak (Yes).
Zostaniesz poproszony o podanie nazwy hosta (hostname) – możesz zostawić domyślne localhost.
Następnie system poprosi o hasła: source password, relay password oraz admin password (tu możesz dać inne hasło). 
Jeśli będziesz to używał tylko w lokalnej domowej sieci ustaw jedno proste hasło (np. mojehaslo987) 
dla wszystkich trzech opcji – będzie ono potrzebne w następnych krokach.
Po zakończeniu instalacji serwer Icecast automatycznie uruchomi się w tle na domyślnym porcie 8000.

Warto wydłużyć czas oczekiwania na pakiety. Otwórz plik konfiguracyjny Icecast:
```
sudo nano /etc/icecast2/icecast.xml
```

Znajdź sekcję <limits> i zmień wartość <source-timeout> na wyższą, na przykład 30 lub 60 sekund:
```
<source-timeout>60</source-timeout>
````

Zrestartuj serwer Icecast, aby zapisać zmiany:
```
sudo systemctl restart icecast2
```

Krok 2: Konfiguracja lokalnego strumienia (asl-broadcastify)

Wykorzystamy usługę asl-broadcastify, ale zamiast do internetu skierujemy ją do naszego lokalnego serwera Icecast.
Przejdź do katalogu konfiguracyjnego:
```
cd /etc/asterisk/broadcastify
```
(patrz też na opis: https://allstarlink.github.io/adv-topics/broadcastify/#configure-asterisk)
Skopiuj szablon konfiguracji dla swojego node'a (**zastąp XXXXXX swoim numerem, np. 63001**):

```
sudo cp 1999.conf.example XXXXXX.conf
np
sudo cp 1999.conf.example 65345.conf
```

Otwórz plik do edycji **XXXXXX wpisz numer Twojego Noda**

```
sudo nano XXXXXX.conf
```


Zmodyfikuj parametry w pliku. Najważniejsze jest skierowanie strumienia na adres lokalny (127.0.0.1):

**XXXXXX wpisz numer Twojego Noda w wierszu XXXXXX.fifo**

```
FIFO=/var/lib/asterisk/XXXXXX.fifo

# Dane lokalnego serwera Icecast
ICECAST_HOST=127.0.0.1
ICECAST_PORT=8000
ICECAST_MOUNT=/asl.mp3
ICECAST_USER=source
ICECAST_PASSWORD=TUTAJ_TWOJE_HASLO_Z_KROKU_1

# Metadane strumienia (możesz wpisać cokolwiek)
STREAM_NAME="Nasluch NODA ASL"
STREAM_DESCRIPTION="Lokalny strumień"
STREAM_URL="localhost"

```

Zapisz plik (Ctrl+O, Enter) i zamknij edytor (Ctrl+X).Włącz i uruchom usługę przesyłania audio:
**XXXXXX wpisz numer Twojego Noda**

```
systemctl enable asl-broadcastify@XXXXXX
systemctl start asl-broadcastify@XXXXXX
```

Krok 3: Powiązanie Asteriska z potokiem audio

Teraz musimy przekazać dźwięk z Asteriska do utworzonego pliku FIFO.
Otwórz plik rpt.conf:

```
nano /etc/asterisk/rpt.conf
```
Znajdź sekcję swojego node'a (np. 
``` [63001] lub [63001](node-main)``` i dopisz w niej linię wskazującą na plik FIFO:

**XXXXXX wpisz numer Twojego Noda**

```
outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/XXXXXX.fifo
```

Zapisz plik i zrestartuj Asteriska:

```
systemctl restart asterisk
```

🛠️ Odblokowanie portu 8000 dla icesact:
w konsoli (SSH) i wpisz poniższe komendy dla narzędzia firewall-cmd:

Dodaj port 8000 dla połączeń TCP na stałe:
```
sudo firewall-cmd --add-port=8000/tcp --permanent
```
Przeładuj konfigurację zapory, aby zmiany natychmiast weszły w życie:

```
sudo firewall-cmd --reload
```

Możesz teraz sprawdzić w przeglądarce wpisując 

```
http://ip_adres_noda:8000
```
Zobaczysz podobną stronę jak niżej obrazek z wykazem dostępu audio via icecast 

link do strumienia audio to który możesz wpisać w config.ini w ASL Dashboard to

```
http://ip_adres_noda:8000/asl.mp3
```

![](https://github.com/radioprj/asl-utils/blob/main/icecast/icecast.png)









