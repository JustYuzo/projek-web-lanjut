#!/usr/bin/env bash
# exit on error
set -o errexit

# Install semua library dari requirements.txt
pip install -r requirements.txt

# Buat folder 'persistent' (tempat database & foto disimpan)
mkdir -p persistent

# Kumpulkan semua file CSS/JS ke folder staticfiles
python manage.py collectstatic --no-input

# Jalankan migrasi database (buat semua tabel di SQLite)
python manage.py migrate --no-input