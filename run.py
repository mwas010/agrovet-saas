"""
Agrovet Automation Software for Luanda Feeds Centre
Entry point for standalone Windows executable.
"""

import os
import sys
import subprocess
import threading
import time
import logging
import signal
from pathlib import Path

# Force import of whitenoise so PyInstaller bundles it
import whitenoise
import whitenoise.middleware

# Force import of luanda_feeds context processors
import luanda_feeds.context_processors

# Change working directory to executable location
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
    os.chdir(BASE_DIR)
    os.environ['AGROVET_DATA_DIR'] = str(BASE_DIR)
else:
    BASE_DIR = Path(__file__).parent

# Configure logging
logging.basicConfig(
    filename=BASE_DIR / 'app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global flag for shutdown
shutdown_flag = threading.Event()
server_instance = None

def find_browser():
    """Find Chrome or Edge browser path."""
    import winreg

    browsers = [
        (r"Software\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe", "Chrome"),
        (r"Software\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe", "Edge"),
    ]

    for reg_path, name in browsers:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if Path(path).exists():
                return path, name
        except WindowsError:
            continue

    # Fallback search paths
    fallback_paths = [
        Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get('LOCALAPPDATA', 'C:\\Users\\Public\\AppData\\Local')) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "Microsoft/Edge/Application/msedge.exe",
    ]

    for path in fallback_paths:
        if path.exists():
            return str(path), path.stem.capitalize()

    return None, None

def check_single_instance():
    """Check if another instance is already running."""
    import win32api
    import win32event
    import winerror

    mutex = win32event.CreateMutex(None, False, "LuandaFeedsCentre_SingleInstance")
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        return False, None
    return True, mutex

def start_server(port=8000):
    """Start Django server with Waitress in background thread."""
    global server_instance
    
    from waitress import serve
    from luanda_feeds.wsgi import application

    def run_server():
        logger.info(f"Starting server on port {port}")
        server_instance = application
        serve(application, host='127.0.0.1', port=port)

    thread = threading.Thread(target=run_server, daemon=False)
    thread.daemon = True  # Allow thread to be stopped
    thread.start()
    time.sleep(1)  # Give server time to start
    return thread

def launch_browser(browser_path, browser_name, url):
    """Launch browser in app mode."""
    profile_dir = BASE_DIR / "browser_profile"
    profile_dir.mkdir(exist_ok=True)

    if browser_name == "Chrome":
        cmd = [
            browser_path,
            f"--app={url}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1280,800",
        ]
    else:  # Edge
        cmd = [
            browser_path,
            f"--app={url}",
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--window-size=1280,800",
        ]

    logger.info(f"Launching {browser_name}")
    # Use CREATE_NO_WINDOW flag to hide console window for child process
    process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
    return process

def wait_for_window_close():
    """Wait for browser window to close."""
    import win32gui

    time.sleep(2)  # Give window time to appear

    while not shutdown_flag.is_set():
        try:
            time.sleep(0.5)
            # Check if any chrome/edge window exists
            found = False
            def enum_handler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'Luanda' in title or '127.0.0.1' in title:
                        ctx['found'] = True
                        ctx['hwnd'] = hwnd

            ctx = {'found': False, 'hwnd': None}
            try:
                win32gui.EnumWindows(enum_handler, ctx)
            except:
                pass

            if not ctx['found']:
                break

        except Exception as e:
            logger.error(f"Error in window check: {e}")
            break

    logger.info("Browser closed, shutting down")

def cleanup():
    """Clean up resources and ensure process exits."""
    global server_instance
    
    logger.info("Cleaning up resources...")
    
    # Terminate browser if still running
    try:
        if browser_process:
            browser_process.terminate()
            browser_process.wait(timeout=3)
    except:
        pass
    
    # Close mutex handle
    if mutex:
        try:
            import win32api
            win32api.CloseHandle(mutex)
        except:
            pass
    
    logger.info("Cleanup complete")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info("Received shutdown signal")
    shutdown_flag.set()

def main():
    """Main entry point."""
    global browser_process, mutex
    
    logger.info("=" * 50)
    logger.info("Luanda Feeds Centre - Agrovet Automation Starting")
    logger.info("=" * 50)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Check single instance
    is_single, mutex = check_single_instance()
    if not is_single:
        logger.error("Another instance is already running")
        print("Another instance is already running. Please close it first.")
        sys.exit(1)

    # Find browser
    browser_path, browser_name = find_browser()
    if not browser_path:
        logger.error("No browser found (Chrome or Edge required)")
        print("Error: Chrome or Edge browser is required but not found.")
        sys.exit(1)

    logger.info(f"Found {browser_name} at {browser_path}")

    # Start server
    server_thread = start_server()

    # Launch browser
    url = "http://127.0.0.1:8000"
    browser_process = launch_browser(browser_path, browser_name, url)

    try:
        wait_for_window_close()
    finally:
        cleanup()
        logger.info("Application closed")
        print("Application closed. Goodbye!")
        # Force exit
        os._exit(0)

if __name__ == '__main__':
    main()
