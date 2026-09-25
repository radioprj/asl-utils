# Polska wersja `/usr/bin/asl-say`

## Instalacja

Skopiuj plik do katalogu `/usr/bin`:

```bash
sudo -s
cp /opt/asl-utils/asl-say/asl-saypl /usr/bin/

Użycie

Polska wersja skryptu korzysta z polskich plików dźwiękowych oraz obsługuje odczyt czasu i daty w języku polskim.
```
asl-saypl -n numer_noda_twojego -w time24
asl-saypl -n numer_noda_twojego -w datetime24
asl-saypl -n numer_noda_twojego -w ip4
```
Dostępne opcje
**time24**

Odczyt aktualnego czasu w formacie 24-godzinnym.

**datetime24**

Odczyt aktualnej daty i czasu w formacie 24-godzinnym.

**ip4**

Odczyt adresu IPv4 przypisanego do noda.



**Uwaga: skrypt wymaga zainstalowanych polskich plików dźwiękowych:**
https://github.com/radioprj/ASL-sound-pl


