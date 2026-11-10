from pycaw.pycaw import AudioUtilities


def change_volume(action: str) -> str:
    devices = AudioUtilities.GetSpeakers()
    volume = devices.EndpointVolume
    current = volume.GetMasterVolumeLevelScalar()

    if action == "up":
        volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
        return f"Volume increased to {round(min(1.0, current + 0.1) * 100)} percent."

    if action == "down":
        volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
        return f"Volume decreased to {round(max(0.0, current - 0.1) * 100)} percent."

    if action == "mute":
        volume.SetMute(1, None)
        return "Volume muted."

    if action == "unmute":
        volume.SetMute(0, None)
        return "Volume unmuted."

    return "Unknown volume command."
