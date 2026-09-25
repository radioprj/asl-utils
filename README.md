## Zestaw skryptów i modyfikacji do ASL 3
 
## asl-say
Zmodyfikowana wersja skryptu korzystająca z polskich plików dźwiękowych do odczytywania czasu, daty oraz adresu IPv4.
 
## mete-alerts
Skrypt udostępniający alerty pogodowe z serwisu burze.dzis.net.
 
## weather
Skrypt podający aktualne informacje pogodowe dla wybranej lokalizacji z wykorzystaniem OpenWeatherMap.
 
## piper-tts
Zmodyfikowana wersja `asl-tts` korzystająca z polskiego modelu głosowego Piper. Służy do zamiany tekstu na mowę (TTS).
 
## saytime
Zmodyfikowana funkcja `SayTime` w `extensions.conf` dla Asteriska, umożliwiająca odczyt aktualnego czasu w języku polskim po wybraniu kodu DTMF `*722`.
 
## scripts
Zestaw różnych skryptów pomocniczych, wykorzystywanych m.in. do:
- podawania aktualnego czasu o pełnych godzinach,
- odczytywania informacji pogodowych o wybranych porach,
- odczytywania alertów meteorologicznych, jeśli są dostępne.
 
## icecast
Opis konfiguracji serwera strumienia audio Icecast na nodzie ASL. Umożliwia słuchanie transmisji w lokalnej sieci za pomocą przeglądarki internetowej.
 
## node-call
Skrypt generujący pliki audio ze znakami wywoławczymi dla wybranego numeru noda. 
Dzięki temu Asterisk może odczytywać znak wywoławczy zamiast numeru noda.
 
.
Wymienione wyżej skrypty korzystają z polskiej wersji plików dźwiękowych dostępnych w repozytorium:

``` 
https://github.com/radioprj/ASL-sound-pl
```
