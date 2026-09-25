
Node Callsign Generator for AllStarLink 3
-----------------------------------------------

Orginalny skryptp https://github.com/hardenedpenguin/asl-misc-scripts by N5LSN

Skrypt node_call.sh (modyfikacja orginału do potrzeb polskich plików dzwiękowych) generuje pliki dźwiękowe zawierające znaki wywoławcze (callsign) węzłów AllStarLink i zapisuje je w katalogu:
```
/usr/local/share/asterisk/sounds/rpt/nodenames
```
Aby mnięc polskie literowanie znków musisz mieć zainstalowane polskie pliki dźwiękowe:
```
https://github.com/radioprj/ASL-sound-pl
```

Skrypt pobiera informacje o nodach z bazy astdb.txt i generuje pliki dźwiękowe zawierające znaki wywoławcze, które mogą być następnie wykorzystywane przez Asterisk zamiast odczytywania numerów nodów.

Po skonfigurowaniu parametru nodenames w pliku rpt.conf, Asterisk będzie odczytywał znak wywoławczy węzła zamiast jego numeru, o ile dla danego noda istnieje odpowiedni plik w katalogu nodenames.

**Pierwsze uruchomienie**

Podczas pierwszego uruchomienia skrypt tworzy pełną bazę plików audio na podstawie aktualnego wykazu węzłów dostępnego w pliku astdb.txt.

Uwaga: Pierwsze uruchomienie może potrwać kilka minut, w zależności od liczby przetwarzanych wpisów.
```
sudo /opt/asl/utils/node_call.sh -a -f
```
**Aktualizacja całego wykazu**

Aby zaktualizować istniejący wykaz wszystkich nodów:
```
sudo /opt/asl/utils/node_call.sh -r
```
**Dodanie pojedynczego noda**

Aby wygenerować plik dla jednego, wybranego noda, zastąp NUMER_NODA odpowiednim numerem:
```
sudo /opt/asl/utils/node_call.sh -n NUMER_NODA -r
```

**Przykład:**
```
sudo /opt/asl/utils/node_call.sh -n 123456 -r
```
**Konfiguracja Asterisk**

Edytuj plik konfiguracyjny rpt.conf:
```
sudo nano /etc/asterisk/rpt.conf
```

Znajdź poniższy wpis:
```
;nodenames = /usr/local/share/asterisk/sounds/custom/nodenames ; Point to alternate nodenames sound directory
```

Następnie usuń znak ; z początku linii i zmień ścieżkę na:
```
nodenames = /usr/local/share/asterisk/sounds/rpt/nodenames ; Point to alternate nodenames sound directory
```
Jesli chcesz zrezygnować z mównia znaków noda zamiast numeru noda wystaczy że przywrócisz znak komentarza ; na początku nodenames = ...

**Restart Asterisk**

Po zapisaniu zmian zrestartuj usługę Asterisk:
```
sudo systemctl restart asterisk
```
**Efekt działania**

Po poprawnej konfiguracji, gdy Asterisk będzie ogłaszał numer noda, odtworzy jego znak wywoławczy zamiast numeru, jeśli odpowiedni plik znajduje się w katalogu:

/usr/local/share/asterisk/sounds/rpt/nodenames


W przypadku braku pliku dla danego noda Asterisk będzie działał zgodnie ze standardową konfiguracją i odczyta numer węzła.



**Opcje skryptu**
```
Opcja	Opis-h	Wyświetla pomoc i listę dostępnych opcji.
-a	Przetwarza wszystkie nody. Tworzy brakujące pliki i pomija już istniejące, chyba że użyto opcji -r.
-i	Dodaje po znaku wywoławczym słowo „node” oraz numer noda.
-n NODE	Przetwarza tylko wskazany numer noda.
-d PATH	Określa katalog docelowy dla wygenerowanych plików.
-j N	Ustawia liczbę równoległych procesów sox wykorzystywanych podczas generowania plików. Domyślnie używana jest liczba rdzeni procesora.
-v	Włącza szczegółowe komunikaty diagnostyczne (tryb verbose).
-f	Pomija pytanie o potwierdzenie wykonania operacji.
-r	Wymusza ponowne wygenerowanie plików nawet wtedy, gdy już istnieją.
-s PATH	Wskazuje katalog zawierający plik astdb.txt.
-p PATH	Określa ścieżkę do poprzedniej bazy danych używanej do wykrywania zmian.
```
**Przykłady użycia**

Pierwsze pełne wygenerowanie całej bazy bez pytania o potwierdzenie:
```
sudo /opt/asl/utils/node_call.sh -a -f
```

Aktualizacja tylko nowych lub zmienionych nodów:
```
sudo /opt/asl/utils/node_call.sh -f
```

Ponowne wygenerowanie pliku dla pojedynczego noda:
```
sudo /opt/asl/utils/node_call.sh -n 40000 -r
```

Wygenerowanie plików dla wszystkich nodów z wymuszeniem odtworzenia istniejących wpisów:
```
sudo /opt/asl/utils/node_call.sh -a -r
```


