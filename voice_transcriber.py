import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import threading
import queue
import time
import webbrowser
import pyperclip
import pyautogui
from pynput import keyboard as pynput_keyboard
from faster_whisper import WhisperModel

# === CONFIG ===
SAMPLE_RATE = 16000
CHANNELS = 1
RECORDING_FILENAME = "recorded.wav"
TRANSCRIPTION_FILENAME = "transcription.txt"
MODEL_SIZE = "medium"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
MIC_BAR_WIDTH = 30

# === Globals ===
recording = True
duration_sec = 0
action_chosen = None


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, flush=True)
    volume_norm = np.linalg.norm(indata) / len(indata)
    level = min(int(volume_norm * 100 * MIC_BAR_WIDTH), MIC_BAR_WIDTH)
    bar = "█" * level + " " * (MIC_BAR_WIDTH - level)
    print(f"\r🎙️ Mic Level: [{bar}]", end="", flush=True)


def record_audio(filename):
    global duration_sec, recording
    q = queue.Queue()

    def _callback(indata, frames, time_info, status):
        q.put(indata.copy())
        audio_callback(indata, frames, time_info, status)

    with sf.SoundFile(filename, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS) as file:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=_callback):
            print("\n🎤 Recording started.")
            print("Press:")
            print("  1 – Show transcription")
            print("  2 – Send to ChatGPT")
            print("  3 – Copy to clipboard")
            print("  4 – Save and exit")
            print("  5 – Cancel (discard)")
            print("Or press Ctrl+C to stop and choose after.")
            start_time = time.time()
            try:
                while recording:
                    file.write(q.get())
            except KeyboardInterrupt:
                print("\n🛑 Recording interrupted by Ctrl+C.")
            finally:
                duration_sec = time.time() - start_time
                recording = False
                print("\n🎤 Recording stopped.")


def transcribe_audio(filename):
    print("🧠 Transcribing...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    start = time.time()
    segments, info = model.transcribe(filename, beam_size=5, best_of=5)
    end = time.time()
    text = " ".join([seg.text for seg in segments])
    rtf = (end - start) / duration_sec
    print("📝 Transcription complete.\n")
    print(text)
    print("\n📊 Stats:")
    print(f" - Input duration       : {duration_sec:.2f} seconds")
    print(f" - Real-time factor     : {rtf:.2f}x")
    print(f" - Transcription time   : {end - start:.2f} seconds")
    print(f" - Output text length   : {len(text)} characters")
    print(f" - Saved to             : {TRANSCRIPTION_FILENAME}")
    with open(TRANSCRIPTION_FILENAME, "w") as f:
        f.write(text)
    return text


def send_to_chatgpt(text):
    print("🌐 Opening ChatGPT and pasting text...")
    webbrowser.get("firefox").open_new_tab("https://chat.openai.com/")
    time.sleep(5)
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")


def handle_key_input_during_recording():
    global action_chosen, recording

    def on_press(key):
        global action_chosen, recording
        try:
            if key.char == '1':
                action_chosen = 1
                recording = False
            elif key.char == '2':
                action_chosen = 2
                recording = False
            elif key.char == '3':
                action_chosen = 3
                recording = False
            elif key.char == '4':
                action_chosen = 4
                recording = False
            elif key.char == '5':
                action_chosen = 5
                recording = False
        except AttributeError:
            pass

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()
    while recording:
        time.sleep(0.1)
    listener.stop()


def post_transcription_menu(text):
    global action_chosen
    if action_chosen is None:
        print("\nWhat would you like to do?")
        print("1. Show transcription (default)")
        print("2. Send to ChatGPT")
        print("3. Copy to clipboard")
        print("4. Save and exit")
        print("5. Cancel (discard)")
        choice = input("Choose (1–5): ").strip()
        action_chosen = int(choice) if choice in '12345' else 1

    if action_chosen == 1:
        print("\n📄 Transcription:\n")
        print(text)
    elif action_chosen == 2:
        send_to_chatgpt(text)
    elif action_chosen == 3:
        pyperclip.copy(text)
        print("📋 Copied to clipboard.")
    elif action_chosen == 4:
        print("💾 Saved and done.")
    elif action_chosen == 5:
        print("❌ Discarded.")
        try:
            os.remove(TRANSCRIPTION_FILENAME)
        except FileNotFoundError:
            pass


def main():
    recorder = threading.Thread(target=record_audio, args=(RECORDING_FILENAME,))
    hotkeys = threading.Thread(target=handle_key_input_during_recording)
    recorder.start()
    hotkeys.start()
    recorder.join()
    hotkeys.join()

    if os.path.exists(RECORDING_FILENAME):
        text = transcribe_audio(RECORDING_FILENAME)
        post_transcription_menu(text)


if __name__ == "__main__":
    main()
