#!/bin/bash

# 1. Instalacja zależności
pip install -r requirements.txt

# 2. Zbieranie plików statycznych 
# (wymagane na Vercel, by poprawnie serwować CSS/JS)
python manage.py collectstatic --noinput

# 3. Uruchomienie migracji bazy danych
python manage.py migrate