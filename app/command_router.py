import subprocess
import webbrowser


APP_COMMANDS = {
    "notepad": {
        "aliases": {"notepad", "note", "notes", "text editor"},
        "executable": ["notepad.exe"],
    },
    "calculator": {
        "aliases": {"calculator", "calculate", "calc"},
        "executable": ["calc.exe"],
    },
    "paint": {
        "aliases": {"paint", "microsoft paint"},
        "executable": ["mspaint.exe"],
    },
}

WEBSITE_COMMANDS = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
}

ACTION_PREFIXES = (
    "open ",
    "launch ",
    "start the ",
    "start ",
    "please open ",
    "please launch ",
    "please start ",
    "can you open ",
    "can you launch ",
    "could you open ",
    "could you launch ",
    "would you open ",
    "would you launch ",
)


def normalize_command(message: str) -> str:
    command = message.lower().strip()
    command = command.strip(" .,!?")
    return " ".join(command.split())


def extract_target(message: str) -> str | None:
    command = normalize_command(message)

    for prefix in ACTION_PREFIXES:
        if command.startswith(prefix):
            target = command[len(prefix):].strip(" .,!?")
            if target:
                return target

    return None


def execute_command(message: str) -> str | None:
    target = extract_target(message)

    if target is None:
        return None

    for app_name, details in APP_COMMANDS.items():
        if target in details["aliases"]:
            try:
                subprocess.Popen(details["executable"], shell=False)
                return f"Opening {app_name}."
            except OSError:
                return f"Could not open {app_name}."

    return None


def open_website(message: str) -> str | None:
    target = extract_target(message)

    if target is None:
        return None

    for site_name, url in WEBSITE_COMMANDS.items():
        if target == site_name:
            try:
                webbrowser.open(url)
                return f"Opening {site_name} in your browser."
            except Exception:
                return f"Could not open {site_name}."

    return None
