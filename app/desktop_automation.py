import subprocess
from pathlib import Path
import pyautogui
import psutil


APP_PROCESSES = {
    "notepad": {
        "process": "notepad.exe",
        "launch": ["notepad.exe"],
    },
    "calculator": {
        "process": "CalculatorApp.exe",
        "launch": ["calc.exe"],
    },
    "paint": {
        "process": "mspaint.exe",
        "launch": ["mspaint.exe"],
    },
}


def take_screenshot() -> str:
    folder = Path("screenshots")
    folder.mkdir(exist_ok=True)

    screenshot_path = folder / "desktop.png"
    pyautogui.screenshot().save(screenshot_path)

    return f"Screenshot saved: {screenshot_path}"


def get_screen_size() -> str:
    width, height = pyautogui.size()
    return f"Screen resolution is {width} by {height}."


def open_application(app_name: str) -> str:
    details = APP_PROCESSES[app_name]

    try:
        subprocess.Popen(details["launch"], shell=False)
        return f"Opening {app_name}."
    except OSError:
        return f"Could not open {app_name}."


def close_application(app_name: str) -> str:
    import ctypes

    process_name = APP_PROCESSES[app_name]["process"]
    target_pids = set()

    for process in psutil.process_iter(["name", "pid"]):
        try:
            name = process.info["name"]

            if name and name.lower() == process_name.lower():
                target_pids.add(process.info["pid"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not target_pids:
        return f"{app_name.capitalize()} is not currently running."

    user32 = ctypes.windll.user32
    WM_CLOSE = 0x0010
    sent = []

    enum_callback_type = ctypes.WINFUNCTYPE(
        ctypes.c_bool,
        ctypes.c_void_p,
        ctypes.c_void_p,
    )

    def callback(hwnd, _):
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

        if pid.value in target_pids:
            if user32.PostMessageW(hwnd, WM_CLOSE, 0, 0):
                sent.append(pid.value)

        return True

    callback_ref = enum_callback_type(callback)
    user32.EnumWindows(callback_ref, 0)

    if sent:
        return f"Safe close request sent to {app_name}. Save any unsaved work if prompted."

    return f"No closable window found for {app_name}. The application may still be running."


def desktop_command(message: str) -> str | None:
    command = " ".join(message.lower().strip(" .,!?").split())

    if command in {"take screenshot", "capture screen", "capture screenshot"}:
        return take_screenshot()

    if command in {"screen size", "display resolution"}:
        return get_screen_size()

    for app_name in APP_PROCESSES:
        if command in {
            f"open {app_name}",
            f"launch {app_name}",
            f"start {app_name}",
            
        }:
            return open_application(app_name)

        if command in {
            f"close {app_name}",
            f"exit {app_name}",
            f"quit {app_name}",
        }:
            return close_application(app_name)

    return None
