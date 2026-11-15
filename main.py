#!/usr/bin/env python3
"""
Chrome Kiosk Mode Launcher
Launches Chrome in kiosk mode pointing to a specific URL with device permissions auto-granted.
"""

import os
import sys
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from pynput import keyboard
from pathlib import Path

base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
load_dotenv(base / ".env")

TARGET_URL = os.getenv("TARGET_URL")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state for keyboard listener
listener = None
escape_attempt_detected = False
keys_pressed = set()


def on_press(key):
    """
    Handle keyboard press events.
    Detect Windows key, Alt+Tab, and Ctrl+Alt+Delete attempts and close Chrome.
    """
    global escape_attempt_detected, keys_pressed

    try:
        # Track which keys are pressed
        keys_pressed.add(key)

        # Detect Windows key (left and right)
        if key == keyboard.Key.cmd or key == keyboard.Key.cmd_r:
            logger.warning("Windows key pressed - closing Chrome")
            escape_attempt_detected = True
            return

        # Detect Alt+Tab
        if key == keyboard.Key.tab:
            if keyboard.Key.alt in keys_pressed or keyboard.Key.alt_l in keys_pressed or keyboard.Key.alt_r in keys_pressed:
                logger.warning("Alt+Tab attempted - closing Chrome")
                escape_attempt_detected = True
                return

        # Detect Ctrl+Alt+Delete
        ctrl_pressed = (keyboard.Key.ctrl in keys_pressed or
                        keyboard.Key.ctrl_l in keys_pressed or
                        keyboard.Key.ctrl_r in keys_pressed)
        alt_pressed = (keyboard.Key.alt in keys_pressed or
                       keyboard.Key.alt_l in keys_pressed or
                       keyboard.Key.alt_r in keys_pressed)
        delete_pressed = (key == keyboard.Key.delete)

        if ctrl_pressed and alt_pressed and delete_pressed:
            logger.warning("Ctrl+Alt+Delete attempted - closing Chrome")
            escape_attempt_detected = True
            return

        # Detect Ctrl+Shift+Escape (Task Manager)
        shift_pressed = (keyboard.Key.shift in keys_pressed or
                         keyboard.Key.shift_l in keys_pressed or
                         keyboard.Key.shift_r in keys_pressed)
        escape_pressed = (key == keyboard.Key.esc)

        if ctrl_pressed and shift_pressed and escape_pressed:
            logger.warning(
                "Ctrl+Shift+Escape (Task Manager) attempted - closing Chrome")
            escape_attempt_detected = True
            return

        # Detect Alt+F4 (close window)
        f4_pressed = (key == keyboard.Key.f4)

        if alt_pressed and f4_pressed:
            logger.warning("Alt+F4 attempted - closing Chrome")
            escape_attempt_detected = True
            return

    except AttributeError:
        pass


def on_release(key):
    """
    Handle keyboard release events.
    Track when keys are released to maintain accurate key state.
    """
    global keys_pressed

    try:
        keys_pressed.discard(key)
    except:
        pass


def start_keyboard_monitor():
    """
    Start a background thread that listens for escape key attempts.
    If Windows key, Alt+Tab, or Ctrl+Alt+Delete are pressed, closes Chrome.
    """
    global listener

    try:
        logger.info(
            "Starting keyboard monitor (detecting Windows key, Alt+Tab, Ctrl+Alt+Delete)...")
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        logger.info("Keyboard monitor active.")
    except Exception as e:
        logger.warning(
            f"Failed to start keyboard monitor: {e}. Continuing without monitoring.")


def stop_keyboard_monitor():
    """
    Stop the keyboard listener thread.
    """
    global listener

    if listener:
        try:
            listener.stop()
            logger.info("Keyboard monitor stopped.")
        except Exception as e:
            logger.warning(f"Error stopping keyboard monitor: {e}")


def configure_chrome_options(url):
    """
    Configure Chrome options for kiosk mode with device permissions auto-granted.
    """
    options = Options()

    # Kiosk mode settings
    options.add_argument("--kiosk")
    options.add_argument("--start-fullscreen")
    options.add_argument(f"--app={url}")

    # Suppress UI elements and dialogs
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-session-crashed-bubble")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-default-apps")

    # Performance and background activity
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-media-suspend")
    options.add_argument("--disable-sync")
    options.add_argument("--disable-translate")

    # Device permissions - auto-grant
    options.add_argument("--auto-accept-camera-and-microphone-capture")

    # Security - disable devtools to prevent navigation bypass
    options.add_argument("--disable-devtools")

    # Hide "Chrome is being controlled by automated test software" banner
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Preferences for additional permissions and media device enumeration
    prefs = {
        "profile.managed_default_content_settings": {
            "geolocation": 1,         # Allow
            "camera": 1,              # Allow
            "microphone": 1,          # Allow
            "notifications": 1,       # Allow
            "media_stream_mic": 1,    # Allow microphone access
            "media_stream_camera": 1,  # Allow camera access
        },
        "profile.default_content_settings": {
            "geolocation": 1,
            "camera": 1,
            "microphone": 1,
            "notifications": 1,
            "media_stream_mic": 1,
            "media_stream_camera": 1,
        },
        # Enable media device enumeration
        "profile.content_settings.exceptions.media_stream_mic": {
            "*": {
                "setting": 1  # Allow microphone
            }
        },
        "profile.content_settings.exceptions.media_stream_camera": {
            "*": {
                "setting": 1  # Allow camera
            }
        },
        # Ensure media devices are accessible
        "hardware.audio_output_enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    return options


def launch_kiosk(url=None):
    """
    Launch Chrome in kiosk mode pointing to the target URL.
    """
    url = url or TARGET_URL
    logger.info(f"Launching Chrome in kiosk mode at: {url}")

    try:
        # Configure Chrome options
        options = configure_chrome_options(url)

        logger.info(
            "Initializing WebDriver with auto-managed Chrome (Selenium will download if needed).")
        driver = webdriver.Chrome(options=options)

        logger.info("Chrome launched successfully in kiosk mode.")
        return driver

    except Exception as e:
        logger.error(f"Failed to launch Chrome: {e}")
        raise


def keep_alive(driver):
    """
    Keep the browser alive and monitor for escape key attempts.
    If Windows key, Alt+Tab, or Ctrl+Alt+Delete are pressed, closes Chrome.
    """
    global escape_attempt_detected

    # Start keyboard monitor
    if os.getenv("MONITOR_ESCAPE_KEYS", "true").lower() == "true":
        start_keyboard_monitor()

    logger.info("Kiosk mode is active. Press Ctrl+C to exit.")

    try:
        while True:
            # Check if escape attempt was detected
            if escape_attempt_detected:
                logger.info("Escape attempt detected. Closing Chrome.")
                break

            # Keep the driver alive by checking if the window is still open
            if not driver.window_handles:
                logger.info("Browser window closed. Exiting.")
                break

            # Small sleep to reduce CPU usage
            import time
            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.info("Interrupt signal received. Shutting down gracefully.")

    except Exception as e:
        logger.warning(f"Error in kiosk loop: {e}")

    finally:
        # Stop keyboard monitor
        stop_keyboard_monitor()

        try:
            driver.quit()
            logger.info("WebDriver closed successfully.")
        except Exception as e:
            logger.warning(f"Error closing WebDriver: {e}")


def main():
    """
    Main entry point for the kiosk launcher.
    """
    logger.info("Chrome Kiosk Mode Launcher started.")

    try:
        driver = launch_kiosk()
        keep_alive(driver)

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

    logger.info("Chrome Kiosk Mode Launcher stopped.")


if __name__ == "__main__":
    main()
