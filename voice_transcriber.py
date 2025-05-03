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
from playsound import playsound
import sys

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
start_time = None
action_chosen = None
callback_enabled = True

def print_help():
    print("""
🎙️ voice_transcriber.py - Record or transcribe voice audio using Whisper

USAGE:
  python3 voice_transcriber.py                   # Start recording interactively
  python3 voice_transcriber.py <audio_file.wav>  # Transcribe existing file (no recording)
  python3 voice_transcriber.py --help            # Show this help message

NOTES:
- Press 1–5 during recording to choose action:
    1: Show transcription
    2: Send to ChatGPT (autotype)
    3: Copy to clipboard
    4: Save and exit
    5: Cancel
""")

def audio_callback(indata, frames, time_info, status):
    global callback_enabled
    if not callback_enabled:
        return
    volume_norm = np.linalg.norm(indata) / len(indata)
    level = min(int(volume_norm * 100 * MIC_BAR_WIDTH), MIC_BAR_WIDTH)
    bar = "█" * level + " " * (MIC_BAR_WIDTH - level)
    elapsed = time.time() - start_time if start_time else 0
    print(f"\r🎤 {elapsed:5.1f}s [{bar}]", end="", flush=True)

def record_audio(filename):
    global duration_sec, recording, callback_enabled, start_time
    q = queue.Queue()

    def _callback(indata, frames, time_info, status):
        q.put(indata.copy())
        audio_callback(indata, frames, time_info, status)

    with sf.SoundFile(filename, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS) as file:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=_callback):
            playsound("sounds/beep.wav")
            print("\n🎤 Recording started.")
            print("Press:")
            print("  1 – Show transcription")
            print("  2 – Send to ChatGPT")
            print("  3 – Copy to clipboard")
            print("  4 – Save and exit")
            print("  5 – Cancel (discard and stop immediately)")
            print("🔍 Press any key to debug its value.\n")

            start_time = time.time()
            try:
                while recording:
                    try:
                        file.write(q.get(timeout=0.1))
                    except queue.Empty:
                        continue
            finally:
                duration_sec = time.time() - start_time
                callback_enabled = False
                print("\r" + " " * (MIC_BAR_WIDTH + 20), end="\r", flush=True)
                print("\n🎤 Recording stopped.")

def transcribe_audio(filename):
    print("🧠 Transcribing...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    start = time.time()
    segments, info = model.transcribe(filename, beam_size=5, best_of=5)
    end = time.time()
    text = " ".join([seg.text for seg in segments])

    global duration_sec
    if duration_sec == 0:
        with sf.SoundFile(filename) as f:
            file_duration = len(f) / f.samplerate
        rtf = (end - start) / file_duration
    else:
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
        k_repr = repr(key)
        print(f"\n🔍 Pressed key: {k_repr}")

        key_map = {
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
        }

        if hasattr(key, 'char') and key.char in key_map:
            action_chosen = key_map[key.char]
            recording = False
            return

        if k_repr in ['<65437>']:
            action_chosen = 5
            recording = False
            return

        vk_map = {
            97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 53: 5, 229: 5
        }
        if hasattr(key, 'vk') and key.vk in vk_map:
            action_chosen = vk_map[key.vk]
            recording = False

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()
    while recording:
        time.sleep(0.05)
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
        print("📅 Saved and done.")
    elif action_chosen == 5:
        print("❌ Discarded.")
        try:
            os.remove(TRANSCRIPTION_FILENAME)
        except FileNotFoundError:
            pass

    input("\n✅ Press Enter to close this window...")

def main():
    if len(sys.argv) > 2 or (len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]):
        print_help()
        return

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        text = transcribe_audio(sys.argv[1])
        post_transcription_menu(text)
        return

    recorder = threading.Thread(target=record_audio, args=(RECORDING_FILENAME,))
    hotkeys = threading.Thread(target=handle_key_input_during_recording)
    recorder.start()
    hotkeys.start()
    recorder.join()
    hotkeys.join()

    if os.path.exists(RECORDING_FILENAME):
        if action_chosen == 5:
            print("❌ Aborted before transcription.")
            return
        text = transcribe_audio(RECORDING_FILENAME)
        post_transcription_menu(text)

if __name__ == "__main__":
    main()
