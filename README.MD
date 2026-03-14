# AI Quiz Generator Platform - Backend

Repozytorium backendowe projektu AI Quiz Generator. System oparty na frameworku Django, wykorzystujący izolację środowisk poprzez `venv`.

## 🛠 Konfiguracja środowiska deweloperskiego

### 1. Klonowanie repozytorium
```bash
git clone <url-repozytorium>
cd AI-Quiz-Generator-Platform-backend
```

### 2. Tworzenie środowiska wirtualnego (Venv)
```powershell
# Windows
py -m venv .venv

# macOS / Linux
python3 -m venv .venv
```

### 3. Aktywacja środowiska
**Windows (PowerShell):**
*(Jeśli pojawi się błąd o blokadzie skryptów, uruchom najpierw: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*
```powershell
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```
*(Sukces: Po lewej stronie w terminalu powinien pojawić się napis `(.venv)`)*

### 4. Instalacja zależności
Gdy środowisko jest aktywne, pobierz wymagane biblioteki (odpowiednik `npm install`):
```bash
pip install -r requirements.txt
```

### 5. Uruchomienie serwera
```bash
python manage.py runserver
```
Aplikacja będzie dostępna w przeglądarce pod adresem: `http://127.0.0.1:8000/`

---

## 🚀 Standardy pracy w zespole

**Dodawanie nowej biblioteki:**
Jeśli instalujesz nową paczkę (np. `pip install djangorestframework`), **musisz** zaktualizować manifest dla reszty zespołu:
1. `pip install <nazwa_paczki>`
2. `pip freeze > requirements.txt`
3. Zrób `git add requirements.txt`, zrób commit i wyślij zmiany na GitHuba.

**Pobieranie zmian od innych:**
Po zrobieniu `git pull`, profilaktycznie zaktualizuj swoje lokalne środowisko:
```bash
pip install -r requirements.txt
```

## ⚠️ Higiena Repozytorium (Ważne!)

1. **NIE WRZUCAJ folderu `.venv`** – jest on ignorowany przez `.gitignore`. Każdy tworzy własny lokalnie.
2. **NIE WRZUCAJ plików `.env`** – zawierają one wrażliwe dane (hasła, klucze API).
3. **Zawsze sprawdzaj `git status` przed commitem.** Jeśli widzisz na liście pliki bazy danych (`db.sqlite3`) lub foldery `__pycache__`, oznacza to, że Twój `.gitignore` nie działa poprawnie – napraw to zanim zrobisz `push`.
4. **Zależności:** Jeśli instalujesz nową bibliotekę, od razu zrób `pip freeze > requirements.txt`.