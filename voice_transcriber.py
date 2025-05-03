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
import subprocess
from pynput import keyboard as pynput_keyboard
from faster_whisper import WhisperModel
from playsound import playsound
import sys
from datetime import datetime

# === CONFIG ===
SAMPLE_RATE = 16000
CHANNELS = 1
MODEL_SIZE = "medium"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
MIC_BAR_WIDTH = 30
CHATGPT_ICON_IMAGE = "assets/chatgpt_plus.jpeg"

# === Globals ===
recording = True
duration_sec = 0
start_time = None
action_chosen = None
callback_enabled = True
RECORDING_FILENAME = "recorded.wav"  # fallback only
TRANSCRIPTION_FILENAME = "transcription.txt"
current_audio_path = None
current_transcript_path = None

def generate_paths():
    now = datetime.now()
    base_folder = os.path.join("recordings", now.strftime("%Y-%m-%d"), now.strftime("%H-%M-%S"))
    os.makedirs(base_folder, exist_ok=True)
    global current_audio_path, current_transcript_path
    current_audio_path = os.path.join(base_folder, "audio.wav")
    current_transcript_path = os.path.join(base_folder, "transcript.txt")
    return current_audio_path

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
    2: Paste into ChatGPT (existing tab)
    3: Open ChatGPT and paste
    4: Save and exit
    5: Cancel
- 📋 Text will always be copied to clipboard automatically.
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
            playsound("sounds/plop.wav")
            print("\n🎤 Recording started.")
            print("Press:")
            print("  1 – Show transcription")
            print("  2 – Paste into ChatGPT (existing tab)")
            print("  3 – Open ChatGPT and paste")
            print("  4 – Save and exit")
            print("  5 – Cancel (discard and stop immediately)")
            print("📋 Text will always be copied to clipboard.\n")

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

def focus_and_click_chatgpt_input(timeout=5):
    try:
        print("🔍 Looking for '+' icon to focus input...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            location = pyautogui.locateOnScreen(CHATGPT_ICON_IMAGE, confidence=0.85)
            if location:
                center = pyautogui.center(location)
                pyautogui.click(center.x, center.y - 40)
                print("✅ Focused input box.")
                return True
            time.sleep(0.1)
        print("❌ '+' icon not found.")
        return False
    except Exception as e:
        print(f"⚠️ Input focus failed: {e}")
        return False

def transcribe_audio(filename):
    print("🧠 Transcribing...")
    model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    start = time.time()
    segments, info = model.transcribe(filename, beam_size=5, best_of=5)
    end = time.time()
    text = " ".join([seg.text for seg in segments])

    pyperclip.copy(text)
    print("📋 Copied to clipboard.")
    playsound("sounds/plop.wav")

    global duration_sec, current_transcript_path
    if duration_sec == 0:
        with sf.SoundFile(filename) as f:
            file_duration = len(f) / f.samplerate
        rtf = (end - start) / file_duration
    else:
        rtf = (end - start) / duration_sec

    print("\n📊 Stats:")
    print(f" - Input duration       : {duration_sec:.2f} seconds")
    print(f" - Real-time factor     : {rtf:.2f}x")
    print(f" - Transcription time   : {end - start:.2f} seconds")
    print(f" - Output text length   : {len(text)} characters")
    print(f" - Saved to             : {current_transcript_path}")
    with open(current_transcript_path, "w") as f:
        f.write(text)
    return text

def send_to_existing_chatgpt(text):
    print("📨 Focusing Firefox window...")
    try:
        subprocess.call(['xdotool', 'search', '--onlyvisible', '--class', 'firefox', 'windowactivate'])
        time.sleep(0.2)
        if focus_and_click_chatgpt_input(timeout=5):
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.1)
            pyautogui.press("enter")
        else:
            print("⚠️ Could not find ChatGPT input box. Message not sent.")
    except Exception as e:
        print(f"❌ Failed to interact with Firefox: {e}")

def send_to_new_chatgpt(text):
    print("🌐 Opening ChatGPT...")
    webbrowser.get("firefox").open_new_tab("https://chat.openai.com/")
    found = focus_and_click_chatgpt_input(timeout=5)
    time.sleep(0.5)
    
        
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
    if not found:
        print("⚠️ Input box not detected, pasted anyway.")

def handle_key_input_during_recording():
    global action_chosen, recording

    def on_press(key):
        global action_chosen, recording
        key_map = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5}
        if hasattr(key, 'char') and key.char in key_map:
            action_chosen = key_map[key.char]
            recording = False
        elif hasattr(key, 'vk') and key.vk in {97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 53: 5, 229: 5}:
            action_chosen = {97: 1, 98: 2, 99: 3, 100: 4, 101: 5, 53: 5, 229: 5}[key.vk]
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
        print("2. Paste into ChatGPT (existing tab)")
        print("3. Open ChatGPT and paste")
        print("4. Save and exit")
        print("5. Cancel (discard)")
        choice = input("Choose (1–5): ").strip()
        action_chosen = int(choice) if choice in '12345' else 1

    print("\n📄 Transcription:\n")
    print(text)
    print()
    if action_chosen == 1:
        pass
    elif action_chosen == 2:
        send_to_existing_chatgpt(text)
    elif action_chosen == 3:
        send_to_new_chatgpt(text)
    elif action_chosen == 4:
        print("📅 Saved and done.")
    elif action_chosen == 5:
        print("❌ Discarded.")
        try:
            os.remove(current_audio_path)
            os.remove(current_transcript_path)
        except FileNotFoundError:
            pass

def main():
    if len(sys.argv) > 2 or (len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]):
        print_help()
        return

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        generate_paths()
        text = transcribe_audio(sys.argv[1])
        post_transcription_menu(text)
        return

    filename = generate_paths()
    recorder = threading.Thread(target=record_audio, args=(filename,))
    hotkeys = threading.Thread(target=handle_key_input_during_recording)
    recorder.start()
    hotkeys.start()
    recorder.join()
    hotkeys.join()

    if os.path.exists(filename):
        if action_chosen == 5:
            print("❌ Aborted before transcription.")
            return
        text = transcribe_audio(filename)
        post_transcription_menu(text)

if __name__ == "__main__":
    main()
