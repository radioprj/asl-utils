
# Polska wersja odczytu aktualnego czasu za pomocą kodu DTMF *722

> Uwaga: wymagane jest zainstalowanie polskich plików dźwiękowych dostępnych w repozytorium:
>
> https://github.com/radioprj/ASL-sound-pl

## Modyfikacja funkcji TIME

Aby odczyt czasu był realizowany w języku polskim, należy zastąpić systemową funkcję `TIME` własną wersją.

Otwórz plik:

```bash
sudo -s
nano /etc/asterisk/extensions.conf


W oryginalnej funkcji TIME zakomentuj wszystkie linie, dodając na początku każdej znak ;:

; Say the time of day
;exten => TIME,1,ExecIfTime(0:00-11:59,*,*,*?Playback(rpt/goodmorning))
; same => n,ExecIfTime(12:00-17:59,*,*,*?Playback(rpt/goodafternoon))
; same => n,ExecIfTime(18:00-23:59,*,*,*?Playback(rpt/goodevening))
; same => n,Playback(rpt/thetimeis)
; same => n,SayUnixTime(RPT_TELEM_TIME(),,HM)
; ;same => n,SayUnixTime(RPT_TELEM_TIME(),,${IF($[${STRFTIME(${UNIXTIME},,%-M) = 0}]?IMp:Ip)})
; same => n,Hangup()


Następnie wklej poniższą polską wersję funkcji bezpośrednio pod zakomentowanym fragmentem:

; Say the time of day - Polska wersja

exten => TIME,1,ExecIfTime(0:00-11:59,*,*,*?Playback(rpt/goodmorning))
 same => n,ExecIfTime(12:00-17:59,*,*,*?Playback(rpt/goodafternoon))
 same => n,ExecIfTime(18:00-23:59,*,*,*?Playback(rpt/goodevening))
 same => n,Playback(rpt/thetimeis)
 same => n,Set(GODZINA=${STRFTIME(${EPOCH},,%H)})
 same => n,Set(MINUTY=${STRFTIME(${EPOCH},,%M)})
 same => n,Playback(digits/ho-${GODZINA})
 same => n,SayNumber(${MINUTY})
 same => n,Hangup()

**Restart Asterisk**

Po zapisaniu zmian należy ponownie uruchomić usługę Asterisk:

sudo systemctl restart asterisk

Test działania

Po wykonaniu powyższych czynności możesz sprawdzić działanie funkcji, wybierając kod DTMF:
```
*722
```

System powinien odczytać aktualny czas w języku polskim z wykorzystaniem zainstalowanych polskich plików dźwiękowych.


