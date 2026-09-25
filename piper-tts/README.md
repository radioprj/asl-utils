# Program do zamiany tekstu na mowę (TTS) dla AllStarLink

Program umożliwia zamianę tekstu na mowę z wykorzystaniem polskiego modelu głosowego Piper. Wygenerowany komunikat może zostać odtworzony przez Asterisk lub zapisany do pliku audio.

## Instalacja

Zainstaluj pakiet `asl3-tts`:

```bash
sudo -s
apt install -y asl3-tts


Następnie skopiuj skrypt asl-tts-pl do katalogu /usr/bin:
```
sudo cp /opt/asl-utils/piper-tts/asl-tts-pl /usr/bin/
```
**Użycie**

Skrypt asl-tts-pl jest zgodny ze składnią oryginalnego polecenia asl-tts.

Przykład wysłania komunikatu na noda:
```
asl-tts-pl -n numer_noda_twojego -t "Test komunikatu"
```
**Dokumentacja**

Więcej informacji o dostępnych opcjach znajdziesz w dokumentacji programu:

man asl-tts




