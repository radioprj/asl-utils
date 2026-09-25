#!/usr/bin/python3
# coding=utf-8
#
# Skrypt do generowanie plikow wav Alertow Meteo
# Pomysl i realizacja SP2ONG 2019-2023
# Przepisanie kodu do python3 SP2ONG 2022
# Modyfikacja pod burze: Maciej Gornicz & SP6TK
# Przerobione z suds na zeep – dziala w Python 3.11 (migracja: ChatGPT 2025)


import os
import sys
import sox
import subprocess
import configparser
from zeep import Client
from zeep.exceptions import Fault

# =========== Konfiguracja ========================
config = configparser.ConfigParser()
config.read(r'/opt/asl-utils/meteo-alerts/alerts.ini')

key = config['ini']['key']
x = config['ini']['lat']
y = config['ini']['lon']
range_detect = config['ini']['range_detect']

# test = "TRUE" -> generuje sztuczne alerty
test = "FALSE"
# ==================================================

# sox combiner
cbn = sox.Combiner()
cbn.convert(samplerate=16000, n_channels=1)

city = ""
auth = "OK"
wsdl_file = 'https://burze.dzis.net/soap.php?WSDL'


def convert_to_ulaw(src_wav, dst_ulaw, volume=0.5):
    """Konwertuje plik WAV (16 kHz) na surowy ULAW 8 kHz mono, wywołując
    bezpośrednio binarkę sox (jak w ręcznym poleceniu):
    sox -v 0.7 src_wav -r 8000 -c 1 -e u-law -t ul dst_ulaw
    -t ul wymusza format wyjściowy niezależnie od rozszerzenia pliku
    (sox nie rozpoznaje ".ulaw" samo z siebie, tylko po jawnym -t ul).
    Wymagane przez ASL3 (Asterisk/svxlink na RPi pracuje w 8 kHz ULAW)."""
    subprocess.run(
        ['sox', '-v', str(volume), src_wav,
         '-r', '8000', '-c', '1', '-e', 'u-law', '-t', 'ul', dst_ulaw],
        check=True
    )


def get_kierunek(k):
    kierunki = {
        'N': "polnocny",
        'NE': "polnocno_wschodni",
        'E': "wschodni",
        'SE': "poludniowo_wschodni",
        'S': "poludniowy",
        'SW': "poludniowo_zachodni",
        'W': "zachodni",
        'NW': "polnocno_zachodni"
    }
    return kierunki.get(k, k)


def get_digi(digi):
    fwav = []
    plen = len(str(digi))
    if plen == 4:
        p = (int(digi / 1000)) * 1000
        fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{p}.wav")
        digi -= p
        plen = len(str(digi))
    if plen == 3:
        p = (int(digi / 100)) * 100
        fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{p}.wav")
        digi -= p
        plen = len(str(digi))
    if plen == 2 and digi >= 20:
        p = (int(digi / 10)) * 10
        fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{p}.wav")
        pp = digi - p
        if pp > 0:
            fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{pp}.wav")
    if plen == 2 and digi < 20:
        fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{digi}.wav")
    if plen == 1 and digi > 0:
        fwav.append(f"/opt/asl-utils/meteo-alerts/digits/{digi}.wav")
    return fwav


def burze_api(key, wsdl_file, city, range_detect):
    try:
        client = Client(wsdl_file)
        if city != "":
            xy = client.service.miejscowosc(city, key)
            ostrzezenia = client.service.ostrzezenia_pogodowe(xy['y'], xy['x'], key)
            burza = client.service.szukaj_burzy(xy['y'], xy['x'], range_detect, key)
        else:
            ostrzezenia = client.service.ostrzezenia_pogodowe(x, y, key)
            burza = client.service.szukaj_burzy(x, y, range_detect, key)
        return ostrzezenia, burza
    except Fault as e:
        print("\nBłąd SOAP:", e)
        return None, None


try:
    ostrzezenia, burza = burze_api(key, wsdl_file, city, range_detect)
    if ostrzezenia is None or burza is None:
        auth = "NO"
except TypeError:
    auth = "NO"
    print('\nBłąd komunikacji z API https://burze.dzis.net\n')

if auth == "OK":
    if test == "TRUE":
        ostrzezenia = {"mroz": 0, "upal": 0, 'wiatr': 2, 'opad': 1, 'burza': 0, 'traba': 0}
        burza = {'okres': 15, 'odleglosc': 19.43, 'kierunek': 'W', 'liczba': 12}

    ost = ["mroz", "upal", 'wiatr', 'opad', 'burza', 'traba']
    fwavArr, fwavArrB = [], []

    for ostrzezenie in ost:
        if ostrzezenia[ostrzezenie] > 0:
            fwavArr.append(f"/opt/asl-utils/meteo-alerts/wav/{ostrzezenie}{ostrzezenia[ostrzezenie]}.wav")

    if burza['liczba'] > 0:
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza.wav")
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza_liczba.wav")
        fwavArrB += get_digi(int(burza['liczba']))
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza_okres.wav")
        fwavArrB += get_digi(int(burza['okres']))
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza_minut.wav")
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza_odleglosc.wav")
        fwavArrB += get_digi(int(burza['odleglosc']))
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/burza_kierunek.wav")
        fwavArrB.append(f"/opt/asl-utils/meteo-alerts/wav/{get_kierunek(str(burza['kierunek']))}.wav")

    for old_file in (
        '/opt/asl-utils/meteo-alerts/status/meteo.wav',
        '/opt/asl-utils/meteo-alerts/status/burza.wav',
        '/opt/asl-utils/meteo-alerts/status/meteo.ulaw',
        '/opt/asl-utils/meteo-alerts/status/burza.ulaw',
    ):
        if os.path.isfile(old_file):
            os.remove(old_file)

    if fwavArr or fwavArrB:
        print("\nGenerowanie pliku WAV z komunikatem meteo:\n")
        fwavArr.insert(0, "/opt/asl-utils/meteo-alerts/wav/alerts_begin.wav")
        if fwavArrB:
            fwavArr += fwavArrB
        fwavArr.append("/opt/asl-utils/meteo-alerts/wav/alerts_end.wav")
        cbn.build(fwavArr, '/opt/asl-utils/meteo-alerts/status/meteo.wav', 'concatenate')
        convert_to_ulaw('/opt/asl-utils/meteo-alerts/status/meteo.wav',
                         '/opt/asl-utils/meteo-alerts/status/meteo.ulaw')
        os.remove('/opt/asl-utils/meteo-alerts/status/meteo.wav')
    else:
        print("\nBrak alertów meteo\n")

    if fwavArrB:
        print("\nGenerowanie pliku WAV z komunikatem burze:\n")
        fwavArrB.append("/opt/asl-utils/meteo-alerts/wav/alerts_end.wav")
        cbn.build(fwavArrB, '/opt/asl-utils/meteo-alerts/status/burza.wav', 'concatenate')
        convert_to_ulaw('/opt/asl-utils/meteo-alerts/status/burza.wav',
                         '/opt/asl-utils/meteo-alerts/status/burza.ulaw')
        os.remove('/opt/asl-utils/meteo-alerts/status/burza.wav')
    else:
        print("\nBrak alertów burzowych\n")

sys.exit()
