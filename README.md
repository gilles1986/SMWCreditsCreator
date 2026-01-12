# SMW Credits Creator

Eine Python Desktop-Anwendung zum Verwalten von Tile-to-Character Mappings für Super Mario World Credits (Lunar Magic), optimiert für RHR (ROM Hack Resources) Baseroms (v5.10+).

## Voraussetzungen

- **Windows** (Die Anwendung ist als Windows-only ausgelegt)
- **Python 3.8+** muss installiert sein.

## Installation für Entwickler

1. **Repository klonen**
   ```bash
   git clone <repository-url>
   cd SMWCreditsCreator
   ```

2. **Virtuelle Umgebung erstellen (Empfohlen)**
   Es wird empfohlen, eine virtuelle Umgebung zu nutzen, um Abhängigkeiten isoliert zu halten.
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Abhängigkeiten installieren**
   Installiere die benötigten Pakete aus der `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

   **Haupt-Abhängigkeiten:**
   - `customtkinter`: Für das moderne UI.
   - `toml`: Zum Parsen und Bearbeiten der `exports.toml` Konfigurationsdateien.

## Starten der Anwendung

Um die Anwendung zu starten, führe `main.py` aus:
```bash
python main.py
```

## Entwicklung

### Projektstruktur
- `app/core/`: Enthält die Logik (Validator, ConfigManager, Mapper).
- `app/ui/`: Enthält die GUI-Komponenten (Fenster, Tabs).
- `tests/`: Enthält Unit-Tests.

### Tests ausführen
Um sicherzustellen, dass alles korrekt funktioniert (besonders nach Änderungen), führe die Tests aus:
```bash
python -m unittest discover tests
```

## Features
- **Projekt Validierung**: Prüft automatisch, ob der gewählte Ordner ein valides RHR Projekt ist.
- **Config Fix**: Erkennt und behebt fehlende Einstellungen in `exports.toml` (`use_text_map16_format`).
- **Mapping Editor**: Einfaches Zuweisen von Hex-IDs zu Buchstaben. Speichern und Laden als JSON.
