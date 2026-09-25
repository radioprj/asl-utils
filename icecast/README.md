Konfiguracja serwera icecast do wysyłania audio strumienia w lokalnej sieci domowej
---------------------------------------------------

Poniżej opis jak uruchomić na swoim ASL nodzie wysyłanie strumienia audio w lokalnej sieci
i słuchanie go w np ASL Dashboard. Pamietaj że audio odbierane via strumien icecast
idzie z opoźnieniem do realnego audio i służy tylko do monitorowania aktyności na nodzie.


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
Jeśli bedziesz to używał tylko w lokalnej domoqwej sieci ustaw jedno proste hasło (np. mojehaslo987) 
dla wszystkich trzech opcji – będzie ono potrzebne w następnych krokach.
Po zakończeniu instalacji serwer Icecast automatycznie uruchomi się w tle na domyślnym porcie 8000.

Krok 2: Konfiguracja lokalnego strumienia (asl-broadcastify)

Wykorzystamy usługę asl-broadcastify, ale zamiast do internetu, skierujemy ją do naszego lokalnego serwera Icecast.
Przejdź do katalogu konfiguracyjnego:bashcd /etc/asterisk/broadcastify
(patrz też na opis: https://allstarlink.github.io/adv-topics/broadcastify/#configure-asterisk)
Skopiuj szablon konfiguracji dla swojego node'a (zastąp TWÓJ_NODE swoim numerem, np. 63001):

```
cp 1999.conf.example TWÓJ_NODE.conf
```

Otwórz plik do edycji:

```
nano TWÓJ_NODE.conf
```
Zmodyfikuj parametry w pliku. Najważniejsze jest skierowanie strumienia na adres lokalny (127.0.0.1):

**TWÓJ_NODE to numer Twojego Noda**

```
FIFO=/var/lib/asterisk/TWÓJ_NODE.fifo

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

```
systemctl enable asl-broadcastify@TWÓJ_NODE
systemctl start asl-broadcastify@TWÓJ_NODE
```

Krok 3: Powiązanie Asteriska z potokiem audio

Teraz musimy przekazać dźwięk z Asteriska do utworzonego pliku FIFO.
Otwórz plik rpt.conf:

```
nano /etc/asterisk/rpt.conf
```
Znajdź sekcję swojego node'a (np. [63001] lub [63001](node-main)) i dopisz w niej linię wskazującą na plik FIFO:

```
outstreamcmd = /usr/libexec/asl3/rpt_audio_writer,/var/lib/asterisk/TWÓJ_NODE.fifo
```

Zapisz plik i zrestartuj Asteriska:

```
systemctl restart asterisk
```

🛠️ Odblokowanie portu 8000 dla icesact:
w konsoli (SSH)Zaloguj się na roota (lub użyj sudo) i wpisz poniższe komendy narzędzia firewall-cmd:Dodaj port 8000 dla połączeń TCP na stałe:bashsudo firewall-cmd --add-port=8000/tcp --permanent

Przeładuj konfigurację zapory, aby zmiany natychmiast weszły w życie:

```
sudo firewall-cmd --reload
```

Możesz teraz sprawdzić w przeglądrace wpisując 

```
http://ip_adres_noda:8000
```
Powinień zobaczyć pdobną strona jak niżej obrazek z wykazem dostępu audio via icecast 

link do strumienia audio to który możesz wpisać w config.ini w ASL Dashboard to

```
http://ip_adres_noda:8000/asl.mp3
```

![](http://github.com/radioprj/asl-utils/icecast.png)







