import logging
import re
import os
import tempfile
import speech_recognition as sr
import pyttsx3
from faster_whisper import WhisperModel

from app.ai.ollama_provider import OllamaProvider
from app.config import load_settings
from app.logging_config import setup_logging
from app.command_router import execute_command, open_website
from app.desktop_automation import desktop_command
from app.memory import ConversationMemory
from app.system_info import get_system_info
from app.volume_control import change_volume


def extract_wake_word(message: str, wake_word: str) -> tuple[bool, str]:
    def normalize(text):
        text = re.sub(r"[^\w\s]", " ", text.lower())
        return " ".join(text.split())

    normalized = normalize(message)
    aliases = {
        normalize(wake_word),
        "hey jar",
    }

    for alias in sorted(aliases, key=len, reverse=True):
        if normalized == alias:
            return True, ""

        if normalized.startswith(alias + " "):
            return True, normalized[len(alias):].strip()

    return False, message


def speak(text):
    import base64
    import subprocess

    print(f"\nJARVIS: {text}\n")
    encoded = base64.b64encode(text.encode("utf-16le")).decode("ascii")

    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$voice.Volume = 100; "
        "$voice.Rate = 0; "
        f"$message = [Text.Encoding]::Unicode.GetString("
        f"[Convert]::FromBase64String('{encoded}')); "
        "$voice.Speak($message); "
        "$voice.Dispose()"
    )

    print("[TTS] Windows speech playback starting...")
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        check=True
    )
    print("[TTS] Windows speech playback completed.")


def transcribe_offline(audio, model, language="auto"):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
        file.write(audio.get_wav_data())
        audio_path = file.name

    try:
        segments, info = model.transcribe(
            audio_path,
            language=None if language.strip().lower() == "auto" else language.strip().lower(),
            beam_size=5,
            vad_filter=False,
            condition_on_previous_text=False,
            initial_prompt=(
                "Hey Jarvis. Hey Jar. BLACKBOX. "
                "My project name is BLACKBOX. "
                "Open calculator. Open Paint. "
                "Close calculator. Close Paint. "
                "What is my project name? "
                "Increase volume. Decrease volume. Exit."
            ),
        )
        segments = list(segments)
        if not segments:
            raise sr.UnknownValueError()

        # Reject likely silence-based hallucinations.
        if all(segment.no_speech_prob >= 0.65 for segment in segments):
            print("Low speech activity detected. Please repeat.")
            raise sr.UnknownValueError()

        result = " ".join(segment.text.strip() for segment in segments).strip()

        if not result:
            raise sr.UnknownValueError()

        return result
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


def main():
    settings = load_settings()
    setup_logging()
    logger = logging.getLogger("jarvis.voice")

    memory = ConversationMemory(max_messages=settings.memory_limit)
    jarvis = OllamaProvider(
        model=settings.ollama_model,
        memory=memory,
    )
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 8
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.non_speaking_duration = 0.4
    print("Loading Faster-Whisper Small model...")
    whisper_model = WhisperModel("small", device="cpu", compute_type="int8")
    print("Offline speech recognition: READY")

    print(f"\n=== {settings.app_name} Voice Assistant ===")
    print("Say 'Hey Jarvis' to activate. Say 'exit' to stop.")
    print("Follow-up questions work for 30 seconds after activation.\n")

    import time
    conversation_seconds = 30
    active_until = 0.0

    try:
        with sr.Microphone(device_index=1) as source:
            print("Calibrating microphone...")
            recognizer.adjust_for_ambient_noise(source, duration=3)
            print("Ready!\n")
            speak("Hello Batman. JARVIS-X is ready.")

            while True:
                try:
                    print("Listening...")
                    audio = recognizer.listen(
                        source, timeout=10, phrase_time_limit=15
                    )
                    print("Recognizing speech...")
                    message = transcribe_offline(audio, whisper_model, settings.default_language)

                    if not message:
                        continue

                    print(f"\nRecognized: {message}")
                    normalized = message.lower().strip(" ,.!?")

                    has_wake_word, message = extract_wake_word(
                        message, settings.wake_word
                    )

                    if not has_wake_word and time.monotonic() > active_until:
                        print(f"Wake word not detected. Say '{settings.wake_word}' first.\n")
                        continue

                    if has_wake_word:
                        if not message:
                            active_until = time.monotonic() + conversation_seconds
                            speak("Yes Batman? I'm listening.")
                            continue

                    if message.lower().strip(" ,.!?") in {"exit", "quit", "stop"}:
                        speak("Goodbye Batman.")
                        break

                    print(f"\nYou: {message}")

                    command_result = execute_command(message)
                    if command_result is None:
                        command_result = open_website(message)
                    if command_result is None:
                        command_result = get_system_info(message)

                    if command_result is None:
                        command_result = desktop_command(message)

                    if command_result is None:
                        normalized_command = " ".join(
                            message.lower().strip(" .,!?").split()
                        )

                        volume_patterns = {
                            "unmute": (
                                "unmute",
                                "unmute volume",
                                "turn on the sound",
                            ),
                            "mute": (
                                "mute",
                                "mute volume",
                                "mute the volume",
                                "turn off the sound",
                            ),
                            "up": (
                                "volume",
                                "volume up",
                                "increase volume",
                                "increase the volume",
                                "turn up volume",
                                "turn up the volume",
                                "raise volume",
                                "raise the volume",
                                "louder",
                                "make it louder",
                                "make the volume louder",
                            ),
                            "down": (
                                "volume down",
                                "decrease volume",
                                "decrease the volume",
                                "turn down volume",
                                "turn down the volume",
                                "lower volume",
                                "lower the volume",
                                "quieter",
                                "make it quieter",
                                "make the volume quieter",
                            ),
                        }

                        action = None
                        for candidate, phrases in volume_patterns.items():
                            if any(
                                normalized_command == phrase
                                or (phrase != "volume" and normalized_command.endswith(" " + phrase))
                                for phrase in phrases
                            ):
                                action = candidate
                                break

                        if action:
                            command_result = change_volume(action)

                    if command_result is not None:
                        speak(command_result)
                        active_until = time.monotonic() + conversation_seconds
                        continue

                    answer = jarvis.generate_response(message)
                    speak(answer)
                    active_until = time.monotonic() + conversation_seconds
                    print("Conversation mode active for 30 seconds.\n")

                except sr.WaitTimeoutError:
                    if time.monotonic() > active_until:
                        print("Wake-word mode active. Say 'Hey Jarvis' to begin.\n")
                    else:
                        print("Conversation mode remains active.\n")
                except sr.UnknownValueError:
                    print("Speech was unclear. Please speak slowly and try again.\n")
                except TimeoutError as error:
                    logger.warning("Speech recognition request timed out: %s", error)
                    print("Internet connection timed out. JARVIS will keep listening. Please try again.\\n")

                except sr.RequestError as error:
                    logger.warning("Speech recognition service failed: %s", error)
                    print(f"Speech service error: {error}")
                    print("JARVIS will keep listening. Please try again.\\n")
                except RuntimeError as error:
                    logger.exception("AI provider failed")
                    print(f"JARVIS error: {error}")
                    break

    except OSError as error:
        logger.exception("Audio device error")
        print(f"Audio device error: {error}")
    except KeyboardInterrupt:
        print("\nJARVIS: Voice mode stopped.")


if __name__ == "__main__":
    main()









