import speech_recognition as sr


def main():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.0

    print("=== JARVIS-X Voice Test ===")

    try:
        with sr.Microphone() as source:
            print("Please stay quiet for 2 seconds...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Speak clearly now: My project is BLACKBOX.")
            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=8,
            )

        print("Converting voice to text...")
        text = recognizer.recognize_google(audio, language="en-US")
        print("Recognized:", text)

    except sr.WaitTimeoutError:
        print("No speech detected. Check your microphone.")
    except sr.UnknownValueError:
        print("Speech was captured but not understood.")
        print("Try speaking louder and closer to the microphone.")
    except sr.RequestError as error:
        print("Internet or recognition service error:", error)
    except OSError as error:
        print("Microphone error:", error)


if __name__ == "__main__":
    main()
