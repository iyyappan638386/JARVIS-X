import psutil
import platform
from datetime import datetime


def normalize(message: str) -> str:
    return " ".join(message.lower().strip(" .,!?").split())


def matches(command: str, phrases: set[str]) -> bool:
    return any(
        command == phrase or command.endswith(" " + phrase)
        for phrase in phrases
    )


def get_system_info(message: str) -> str | None:
    command = normalize(message)

    battery_commands = {
        "battery",
        "battery status",
        "check battery",
        "battery percentage",
        "what is my battery status",
        "what is the battery status",
        "tell me my battery status",
        "how much battery is left",
        "how much battery do i have",
        "how much battery do i have left",
        "check my battery",
        "is my laptop charging",
        "is the laptop charging",
        "tell me my battery percentage",
    }

    cpu_commands = {
        "cpu",
        "cpu usage",
        "check cpu",
        "check cpu usage",
        "what is my cpu usage",
        "how much cpu am i using",
        "how much processor am i using",
        "processor usage",
        "check processor usage",
    }

    ram_commands = {
        "ram",
        "memory usage",
        "check memory",
        "what is my ram usage",
        "check ram usage",
        "how much ram am i using",
        "how much memory am i using",
        "check my memory usage",
    }

    system_commands = {
        "system info",
        "computer info",
        "system information",
        "computer information",
        "what is my system information",
        "tell me my computer information",
        "tell me about my computer",
    }

    if matches(command, battery_commands):
        battery = psutil.sensors_battery()
        if battery is None:
            return "Battery information is not available."

        status = "charging" if battery.power_plugged else "not charging"
        return f"Battery is at {battery.percent} percent and {status}."

    if matches(command, cpu_commands):
        usage = psutil.cpu_percent(interval=1)
        return f"CPU usage is {usage} percent."

    if matches(command, ram_commands):
        memory = psutil.virtual_memory()
        used_gb = memory.used / (1024 ** 3)
        total_gb = memory.total / (1024 ** 3)

        return (
            f"RAM usage is {memory.percent} percent. "
            f"{used_gb:.1f} GB used out of {total_gb:.1f} GB."
        )

    if matches(command, system_commands):
        return f"You are running {platform.system()} {platform.release()}."


    time_commands = {
        "time",
        "current time",
        "what time is it",
        "tell me the time",
        "what is the time",
    }

    date_commands = {
        "date",
        "today",
        "today date",
        "what is today's date",
        "what is the date today",
        "tell me today's date",
    }

    day_commands = {
        "one day is today",
        "what day is today",
        "what day is it",
        "which day is today",
    }

    if matches(command, time_commands):
        return f"The current time is {datetime.now().strftime('%I:%M %p')}."

    if matches(command, day_commands):
        return f"Today is {datetime.now().strftime('%A')}."

    if matches(command, date_commands):
        return f"Today's date is {datetime.now().strftime('%B %d, %Y')}."

    return None
