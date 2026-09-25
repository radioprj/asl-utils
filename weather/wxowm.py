#!/usr/bin/python3
# coding=utf-8
#
# SP2ONG wx - skrypt pogodowy dla openweathermap.org
# Port z Perl (wx.pl) na Python, generuje gotowy plik audio
# (WAV 16kHz -> ULAW 8kHz) zamiast pliku sterujacego .tcl dla svxlink,
# przeznaczony do odtworzenia w Asterisk/ASL3.
#
# Wymagane:
#   pip install requests   (lub: apt install python3-requests)
#   sox (system, do sklejania i konwersji plikow audio)
#
# Wymaga wx.ini z apikey/lat/lon (obslugiwany zarowno stary format
# perlowy $apikey="..."; jak i klasyczny [wx] apikey=... w INI).

import os
import sys
import subprocess
import configparser
import requests

# =========== Konfiguracja ========================
INI_PATH = "/opt/asl-utils/weather/wxowm.ini"

WAV_DIR = "/opt/asl-utils/weather/wav"
DIGITS_DIR = "/opt/asl-utils/weather/digits"

OUT_WAV = "/opt/asl-utils/weather/status/wx.wav"
OUT_ULAW = "/opt/asl-utils/weather/status/wx.ulaw"
# ==================================================


def load_config(path):
    """Wczytuje key/lat/lon z pliku INI w formacie zgodnym z alerts.ini:
    [ini]
    key=...
    lat=...
    lon=...
    """
    parser = configparser.ConfigParser()
    parser.read(path)

    if not parser.has_section("ini"):
        raise RuntimeError(f"Brak sekcji [ini] w {path}")

    missing = [k for k in ("key", "lat", "lon") if not parser.has_option("ini", k)]
    if missing:
        raise RuntimeError(f"Brak w konfiguracji [ini]: {', '.join(missing)} ({path})")

    return {
        "apikey": parser["ini"]["key"],
        "lat": parser["ini"]["lat"],
        "lon": parser["ini"]["lon"],
    }


# ============ Wymowa liczb (port z TCL spellNumber/playTwoDigitNumber/ ==
# ============ playThreeDigitNumber/playNumber/playPressure) =============

def _digit_file(name):
    return os.path.join(DIGITS_DIR, f"{name}.wav")


def spell_number(number, out):
    for ch in str(number):
        out.append(_digit_file("decimal") if ch == "." else _digit_file(ch))


def play_two_digit_number(number, out):
    number = str(number).zfill(2)
    first, second = number[0], number[1]
    if first == "0" and second == "0":
        return
    if first == "0":
        out.append(_digit_file(second))
    elif first == "1" or second == "0":
        out.append(_digit_file(number))
    else:
        out.append(_digit_file(f"{int(first) * 10}"))
        out.append(_digit_file(second))


def play_three_digit_number(number, out):
    number = str(number).zfill(3)
    first = number[0]
    if first == "0":
        spell_number(number, out)
    else:
        out.append(_digit_file(f"{first}00"))
        play_two_digit_number(number[1:3], out)


def play_number(value, out=None):
    if out is None:
        out = []
    s = str(value)
    if "." in s:
        integer_part, _, fraction_part = s.partition(".")
        play_number(integer_part, out)
        out.append(_digit_file("decimal"))
        spell_number(fraction_part, out)
        return out

    while s:
        ln = len(s)
        if ln == 1:
            out.append(_digit_file(s))
            s = ""
        elif ln % 2 == 0:
            play_two_digit_number(s[0:2], out)
            s = s[2:]
        else:
            play_three_digit_number(s[0:3], out)
            s = s[3:]
    return out


def play_pressure(value, out=None):
    if out is None:
        out = []
    s = str(value)
    if "." in s:
        integer_part, _, fraction_part = s.partition(".")
        play_number(integer_part, out)
        out.append(_digit_file("decimal"))
        spell_number(fraction_part, out)
        return out

    while s:
        ln = len(s)
        if ln == 1:
            out.append(_digit_file(s))
            s = ""
        elif ln == 3:
            out.append(_digit_file("900"))
            play_two_digit_number(s[1:3], out)
            s = ""
        elif ln == 4:
            out.append(_digit_file("1000"))
            play_two_digit_number(s[2:4], out)
            s = ""
        elif ln % 2 == 0:
            play_two_digit_number(s[0:2], out)
            s = s[2:]
        else:
            play_three_digit_number(s[0:3], out)
            s = s[3:]
    return out


# ============ Kategoryzacja wiatru (1:1 z wx.pl) =========================

def wind_speed_word(winds):
    if winds <= 0.2:
        return "bezwietrznie"
    if winds <= 1.5:
        return "powiew"
    if winds <= 3.3:
        return "slaby"
    if winds <= 5.4:
        return "lagodny"
    if winds <= 7.9:
        return "umiarkowany"
    if winds <= 10.7:
        return "dosc_silny"
    if winds <= 13.8:
        return "silny"
    if winds <= 17.1:
        return "bardzo_silny"
    if winds <= 20.7:
        return "wichura"
    if winds <= 24.4:
        return "silny_sztorm"
    if winds <= 28.4:
        return "bardzo_silny_sztorm"
    if winds <= 32.6:
        return "gwaltowny_silny_sztorm"
    return "huragan"


def wind_dir_word(windd):
    windd = int(windd)
    if windd <= 22 or windd > 337:
        return "polnocny"
    if windd <= 66:
        return "polnocno_wschodni"
    if windd <= 112:
        return "wschodni"
    if windd <= 157:
        return "poludniowo_wschodni"
    if windd <= 202:
        return "poludniowy"
    if windd <= 247:
        return "poludniowo_zachodni"
    if windd <= 292:
        return "zachodni"
    return "polnocno_zachodni"


def uv_word(uvi):
    if uvi < 3.0:
        return "uv_low"
    if uvi < 6.0:
        return "uv_medium"
    if uvi < 8.9:
        return "uv_high"
    if uvi <= 11:
        return "uv_very_high"
    return "uv_extreme"


# ============ Konwersja WAV -> ULAW (jak w alerts.py) ====================

def convert_to_ulaw(src_wav, dst_ulaw, volume=0.5):
    subprocess.run(
        ["sox", "-v", str(volume), src_wav,
         "-r", "8000", "-c", "1", "-e", "u-law", "-t", "ul", dst_ulaw],
        check=True,
    )


# ============ Budowa komunikatu ===========================================

def wav(name):
    return os.path.join(WAV_DIR, f"{name}.wav")


def build_playlist(d):
    play = [wav("wx")]

    main = d["main"]
    wind = d.get("wind", {})
    weather0 = d["weather"][0]

    temp = int(main["temp"])
    temp_feels = int(main["feels_like"])
    hum = main["humidity"]
    pres = int(main["pressure"])
    winds = wind.get("speed", 0.0)
    windd = wind.get("deg")
    weatherid = weather0["id"]
    rain = d.get("rain", {}).get("1h")
    snow = d.get("snow", {}).get("1h")
    uvi = 0  # brak danych UV w API v2.5, jak w oryginale

    rain = 0 if not rain else round(rain, 1)
    snow = 0 if not snow else round(snow, 1)

    # -- temperatura --
    play.append(wav("temp_air"))
    if temp < 0:
        play.append(wav("minus"))
    play_number(abs(temp), play)

    if temp != temp_feels:
        play.append(wav("temp_air_feels"))
        if temp_feels < 0:
            play.append(wav("minus"))
        play_number(abs(temp_feels), play)

    # -- wilgotnosc --
    play.append(wav("humidity"))
    play_number(hum, play)
    play.append(wav("percent"))

    # -- cisnienie --
    play.append(wav("pressure"))
    play_pressure(pres, play)
    play.append(wav("unit_hPa"))

    # -- wiatr: predkosc (opisowo) --
    play.append(wav("wind_speed"))
    play.append(wav(wind_speed_word(winds)))

    # -- wiatr: kierunek --
    if windd is not None:
        play.append(wav("wind_deg"))
        play.append(wav(wind_dir_word(windd)))

    # -- kod zjawiska pogodowego (OpenWeatherMap id) --
    play.append(wav(str(weatherid)))

    # -- opad --
    if rain and rain > 0:
        play.append(wav("rain"))
        play_number(rain, play)
    if snow and snow > 0:
        play.append(wav("snow"))
        play_number(snow, play)

    # -- UV (nieaktywne w API v2.5, zostawione na przyszlosc) --
    if uvi > 0:
        play.append(wav("uv"))
        play.append(wav(uv_word(uvi)))

    return play


def cleanup_outputs():
    for f in (OUT_WAV, OUT_ULAW):
        if os.path.isfile(f):
            os.remove(f)


def fail(message):
    print(message)
    cleanup_outputs()
    try:
        nodata = wav("wx_nodata")
        if os.path.isfile(nodata):
            subprocess.run(["sox", nodata, OUT_WAV], check=True)
            convert_to_ulaw(OUT_WAV, OUT_ULAW)
            os.remove(OUT_WAV)
    except Exception as e:
        print(f"Nie udalo sie zbudowac komunikatu wx_nodata: {e}")
    sys.exit(1)


def main():
    cfg = load_config(INI_PATH)

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?lat={cfg['lat']}&lon={cfg['lon']}&lang=pl&units=metric&appid={cfg['apikey']}"
    )

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        fail(f"UWAGA: Problem z pobraniem danych z serwisu OpenWeatherMap - moze zly API key? ({e})")
        return

    cleanup_outputs()

    playlist = build_playlist(data)

    missing = [p for p in playlist if not os.path.isfile(p)]
    if missing:
        print("UWAGA: brakuje plikow audio:")
        for m in missing:
            print(f"  {m}")

    print("\nGenerowanie pliku WAV z komunikatem pogodowym:\n")
    tmp_wav = OUT_WAV + ".tmp.wav"
    subprocess.run(["sox"] + playlist + [tmp_wav], check=True)
    os.replace(tmp_wav, OUT_WAV)

    convert_to_ulaw(OUT_WAV, OUT_ULAW)
    os.remove(OUT_WAV)
    print(f"OK: {OUT_ULAW}")


if __name__ == "__main__":
    main()
