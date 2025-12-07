#!/usr/bin/env bash
# Başlatıcı: uygulamayı konsol penceresi göstermeden arka planda çalıştırır
DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "$DIR/kirmizi_quickbuttons.py" >/dev/null 2>&1 &
disown
