from unittest.mock import patch, MagicMock

from app.system_info import get_system_info


def test_battery_status():
    battery = MagicMock()
    battery.percent = 91
    battery.power_plugged = True

    with patch("app.system_info.psutil.sensors_battery", return_value=battery):
        result = get_system_info("What is my battery status?")

    assert result == "Battery is at 91 percent and charging."


def test_battery_not_charging():
    battery = MagicMock()
    battery.percent = 50
    battery.power_plugged = False

    with patch("app.system_info.psutil.sensors_battery", return_value=battery):
        result = get_system_info("Is my laptop charging?")

    assert result == "Battery is at 50 percent and not charging."


def test_battery_unavailable():
    with patch("app.system_info.psutil.sensors_battery", return_value=None):
        result = get_system_info("battery status")

    assert result == "Battery information is not available."


def test_cpu_usage():
    with patch("app.system_info.psutil.cpu_percent", return_value=25.5):
        result = get_system_info("How much CPU am I using?")

    assert result == "CPU usage is 25.5 percent."


def test_ram_usage():
    memory = MagicMock()
    memory.used = 8 * (1024 ** 3)
    memory.total = 16 * (1024 ** 3)
    memory.percent = 50.0

    with patch("app.system_info.psutil.virtual_memory", return_value=memory):
        result = get_system_info("How much RAM am I using?")

    assert result == (
        "RAM usage is 50.0 percent. "
        "8.0 GB used out of 16.0 GB."
    )


def test_system_information():
    with patch("app.system_info.platform.system", return_value="Windows"), \
         patch("app.system_info.platform.release", return_value="11"):
        result = get_system_info("Tell me about my computer")

    assert result == "You are running Windows 11."


def test_unknown_command():
    result = get_system_info("Tell me a joke")

    assert result is None

from datetime import datetime
from unittest.mock import patch


def test_current_time():
    fixed = datetime(2026, 11, 10, 14, 30)
    with patch("app.system_info.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed
        result = get_system_info("What time is it?")
    assert result == "The current time is 02:30 PM."


def test_today_date():
    fixed = datetime(2026, 11, 10)
    with patch("app.system_info.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed
        result = get_system_info("What is today's date?")
    assert result == "Today's date is November 10, 2026."


def test_today_day():
    fixed = datetime(2026, 11, 10)
    with patch("app.system_info.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed
        result = get_system_info("What day is today?")
    assert result == "Today is Tuesday."


def test_whisper_day_recognition_alias():
    fixed = datetime(2026, 11, 10)
    with patch("app.system_info.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed
        result = get_system_info("One day is today")
    assert result == "Today is Tuesday."
