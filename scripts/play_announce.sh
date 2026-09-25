#!/bin/bash

# --- KONFIGURACJA ---
NODE="12345"                                 # Wpisz swój numer węzła AllStarLink

AUDIO_DIR="/var/lib/asterisk/sounds/custom" # Ścieżka do Twoich plików audio

# Opcja A: Odtwarzanie jednego konkretnego pliku (usuń '#' aby włączyć)
# SOUND_FILE="identyfikator"

# Opcja B: Losowy wybór pliku z katalogu (zakłada pliki bez rozszerzenia w komendzie rpt)
SOUND_FILE=$(find "$AUDIO_DIR" -type f \( -name "*.ulaw" -o -name "*.gsm" -o -name "*.wav" \) | shuf -n 1 | xargs basename | sed 's/\.[^.]*$//')
# --------------------

# Sprawdzenie czy znaleziono plik
if [ -z "$SOUND_FILE" ]; then
    echo "Błąd: Nie znaleziono plików audio w $AUDIO_DIR"
    exit 1
fi

# Wywołanie komendy Asteriska do odtworzenia lokalnego (localplay)
# Użyj "localplay" aby dźwięk poszedł tylko w eter, lub "playback" aby poszedł też do linków
/usr/sbin/asterisk -rx "rpt localplay $NODE custom/$SOUND_FILE"
