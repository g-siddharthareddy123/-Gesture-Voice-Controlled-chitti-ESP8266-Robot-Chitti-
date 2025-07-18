import speech_recognition as sr
import time

recognizer = sr.Recognizer()
mic = sr.Microphone()

def interpret_command(command):
    command = command.lower()
    if "forward" in command or "front" in command:
        return "F"
    elif "back" in command:
        return "B"
    elif "left" in command:
        return "L"
    elif "right" in command:
        return "R"
    elif "stop" in command:
        return "S"
    else:
        return None

def main():
    print("\n🎤 Say commands like: 'go left', 'go back', 'stop', etc.\n")

    while True:
        try:
            with mic as source:
                print("🎧 Listening for 3 seconds...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, phrase_time_limit=3)

            try:
                text = recognizer.recognize_google(audio)
                print(f"🗣️ You said: {text}")
                cmd = interpret_command(text)
                if cmd:
                    print(f"✅ Command detected: {cmd}")
                else:
                    print("❗ Unknown command. Try: go forward, go left, etc.")
            except sr.UnknownValueError:
                print("😕 Didn't catch that. Speak clearly.")
            except sr.RequestError as e:
                print(f"🔌 Request failed: {e}")

        except KeyboardInterrupt:
            print("🛑 Exiting.")
            break

if __name__ == "__main__":
    main()
