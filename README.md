# SMW Credits Creator

A Python desktop application for managing Tile-to-Character Mappings for Super Mario World Credits (Lunar Magic), optimized for RHR (ROM Hack Resources) Baseroms (v5.10+).

## Features

- **Project Validation**: Automatically checks if the selected folder is a valid RHR project.
- **Config Fix**: Detects and fixes missing settings in `exports.toml` (specifically `use_text_map16_format`).
- **Mapping Editor**: Easily assign Hex IDs to characters with a visual interface. Save and load mappings as JSON.
- **Input Validation**: Real-time hex validation on all tile ID fields with visual feedback (green/red borders). Invalid values are caught at entry, load, bulk edit, and export time.
- **Map16 Generation**: Generates `.map16` files compatible with Lunar Magic's 16x16 Tile Map Editor.
- **Custom Font Support**: Supports 8x8, 8x16, and 16x16 tile sizes.
- **Integration**: Import credits directly from Saphros SMW Credits Manager files (.json).

## Requirements

- **Windows** (The application is designed for Windows)
- **Python 3.8+** must be installed.

## Installation for Developers

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd SMWCreditsCreator
   ```

2. **Create a Virtual Environment (Recommended)**
   It is recommended to use a virtual environment to keep dependencies isolated.
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   Install the required packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

   **Main Dependencies:**
   - `customtkinter`: For the modern UI.
   - `toml`: For parsing and editing `exports.toml` configuration files.
   - `Pillow`: For image processing.
   - `pygame`: For audio/input handling (if used).
   - `pyinstaller`: For building the executable.

## Running the Application

To start the application, run `main.py`:
```bash
python main.py
```

## Building the Executable

To create a standalone `.exe` file for distribution:

1. Ensure all dependencies are installed (including `pyinstaller`).
2. Run the build script:
   ```bash
   python build_exe.py
   ```
3. The executable will be created in the `dist` folder.
   - The script automatically bundles necessary resources (like `palette.pal`, `user_manual.html`, etc.) into the `dist` folder.

## Development

### Project Structure
- `app/core/`: Contains core logic (Validator, ConfigManager, Mapper, Map16Handler).
- `app/ui/`: Contains GUI components (Windows, Tabs).
- `tests/`: Contains unit tests.

### Running Tests
To ensure everything works correctly (especially after changes), run the tests:
```bash
python -m unittest discover tests
```

## Changelog

### v1.2.0
- **Input Validation**: Added comprehensive hex tile ID validation across all layers (UI fields, JSON load/save, bulk editor, export). Invalid values like blank entries or non-hex strings are now caught with visual feedback (red/green borders) instead of silently producing garbled output.
- **Bug Fixes**: Fixed dead code paths in mapper, orphaned parse block in map16_handler, clipboard false-positive return, and 6 broken tests.
- **Code Quality**: Replaced all bare `except:` blocks with specific exception types across 10 files. Replaced all `print()` debug statements with proper `logging` calls.
- **Performance**: Config saves are now batched (1 disk write instead of 8 per save).
- **Refactoring**: Broke apart 240-line tile packing method into focused helper methods, eliminating duplicate code.
