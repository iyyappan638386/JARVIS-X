
import ctypes
from types import SimpleNamespace
from app import desktop_automation


def test_close_application_when_not_running(monkeypatch):
    monkeypatch.setattr(
        desktop_automation.psutil,
        "process_iter",
        lambda *args, **kwargs: [],
    )
    result = desktop_automation.close_application("paint")
    assert result == "Paint is not currently running."


def test_close_application_sends_wm_close(monkeypatch):
    class FakeProcess:
        info = {"name": "mspaint.exe", "pid": 1234}

    class FakeUser32:
        def __init__(self):
            self.close_messages = []

        def EnumWindows(self, callback, _):
            callback(100, 0)
            return True

        def GetWindowThreadProcessId(self, hwnd, pid_pointer):
            pid_pointer._obj.value = 1234
            return 1

        def PostMessageW(self, hwnd, message, wparam, lparam):
            self.close_messages.append((hwnd, message))
            return True

    fake_user32 = FakeUser32()

    monkeypatch.setattr(
        desktop_automation.psutil,
        "process_iter",
        lambda *args, **kwargs: [FakeProcess()],
    )
    monkeypatch.setattr(
        ctypes,
        "windll",
        SimpleNamespace(user32=fake_user32),
        raising=False,
    )

    result = desktop_automation.close_application("paint")

    assert result.startswith("Safe close request sent to paint.")
    assert fake_user32.close_messages == [(100, 0x0010)]


def test_close_application_when_no_window_found(monkeypatch):
    class FakeProcess:
        info = {"name": "mspaint.exe", "pid": 1234}

    class FakeUser32:
        def EnumWindows(self, callback, _):
            return True

    monkeypatch.setattr(
        desktop_automation.psutil,
        "process_iter",
        lambda *args, **kwargs: [FakeProcess()],
    )
    monkeypatch.setattr(
        ctypes,
        "windll",
        SimpleNamespace(user32=FakeUser32()),
        raising=False,
    )

    result = desktop_automation.close_application("paint")

    assert "No closable window found" in result
