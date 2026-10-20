
import subprocess
import sys


def test_jarvis_starts_successfully():
    result = subprocess.run(
        [sys.executable, "app/main.py"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "JARVIS-X is starting..." in result.stdout
    assert "Status: Foundation initialized." in result.stdout
