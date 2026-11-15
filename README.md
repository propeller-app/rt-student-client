# Chrome Kiosk Mode Launcher

This is complete vibe coding, including the massive Readme.

A Python program that launches Google Chrome in kiosk mode, locking the browser to a specific website in fullscreen with all device permissions auto-granted.

## Features

- ✅ Detects existing Chrome installation on Windows
- ✅ Auto-downloads Chrome if not installed (via Selenium)
- ✅ Launches in kiosk mode (fullscreen, no UI chrome)
- ✅ Locks navigation to target URL (prevents leaving the website)
- ✅ Auto-grants all device permissions (camera, microphone, geolocation, notifications)
- ✅ Suppresses popups, dialogs, and extension UI
- ✅ Packagable as standalone .exe via auto-py-to-exe

## Requirements

- **OS:** Windows 10/11
- **Python:** 3.8 or higher
- **Internet connection** (for Chrome download if needed)

## Installation

### Step 1: Clone or download this repository

```bash
cd rt-student-client
```

### Step 2: Install Python dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running as Python Script

```bash
python main.py
```

The script will:

1. Detect Chrome or download it if not present
2. Launch Chrome in kiosk mode pointing to website in .env TARGET_URL
3. Run in fullscreen with device permissions auto-granted
4. Keep running until you press **Ctrl+C** to exit

### Building as Standalone .exe

#### Using auto-py-to-exe GUI:

```bash
auto-py-to-exe
```

1. In the GUI, select:
   - **Script Location:** Point to `main.py`
   - **Onefile:** Check this box (creates single .exe)
   - **Window Based:** Check this box (hides console window) - optional
   - **Output Location:** Choose output directory
   - **Icon File:** (optional) Add a custom icon

2. Click **CONVERT .PY TO .EXE**

3. The resulting `.exe` file will be in the output directory and can run on any Windows machine without Python installed

#### Alternative: Command-line approach

```bash
python -m PyInstaller --onefile --noconsole --collect-all selenium `
  --hidden-import pynput.keyboard._win32 `
  --hidden-import pynput.mouse._win32 `
  --add-data ".env;." `
  main.py
```

This creates `dist/main.exe` that can be distributed and run independently.

## Configuration

To change the target URL, edit `.env` and modify the `TARGET_URL` variable:

```python
TARGET_URL = "https://your-desired-url.com"
```

Then rebuild the .exe if needed.

## Exit & Control

- **Exit the kiosk:** Press **Ctrl+C** in the terminal (or Alt+F4 to close the Chrome window directly)
- **Task Manager:** If needed, you can force-close via Windows Task Manager

## Security Notes

- The `--app` flag locks the browser to the target URL but prevents most navigation
- DevTools are disabled to prevent advanced users from bypassing the URL lock
- All device permissions are auto-granted (camera, microphone, geolocation, etc.)
- Popups and extensions are disabled
- Consider this a "soft" kiosk mode suitable for controlled environments (e.g., classroom kiosks)

## Development

### Project Structure

```
rt-student-client/
├── main.py              # Core launcher script
├── requirements.txt     # Python dependencies
├── README.md           # This file
```

### Dependencies

- **Selenium:** WebDriver for Chrome automation
- **auto-py-to-exe:** GUI wrapper for PyInstaller to build .exe

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions, contact the development team.
