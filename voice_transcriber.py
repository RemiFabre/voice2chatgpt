import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
import numpy as np
import os
import time
import argparse
import signal
import sys
import threading
import shutil

# Optional normalizer (manual install required)
try:
    from whisper.normalizers.english import EnglishTextNormalizer
    NORMALIZER_AVAILABLE = True
    normalizer = EnglishTextNormalizer()
except ImportError:
    NORMALIZER_AVAILABLE = False
    normalizer = lambda x: x

# === CONFIG ===
AUDIO_FILENAME = "recorded.wav"
TEXT_FILENAME = "transcription.txt"
SAMPLERATE = 16000
CHANNELS = 1
USE_NORMALIZER = False  # Set to False to disable punctuation cleanup
BAR_WIDTH = 30

# === STATE ===
audio_buffer = []
record_start_time = None
recording = True
last_volume_bar = ""

def callback(indata, frames, time_info, status):
    global last_volume_bar
    if recording:
        audio_buffer.append(indata.copy())
        rms = np.sqrt(np.mean(indata**2))
        bar_length = min(int(rms * BAR_WIDTH * 10), BAR_WIDTH)
        volume_bar = "[" + "█" * bar_length + " " * (BAR_WIDTH - bar_length) + "]"
        if volume_bar != last_volume_bar:
            print(f"\r🎙️ Mic Level: {volume_bar}", end="", flush=True)
            last_volume_bar = volume_bar

def start_immediate_recording():
    global audio_buffer, record_start_time
    audio_buffer = []
    record_start_time = time.time()
    print("🎙️  Recording started. Press Ctrl+C to stop.")

    try:
        with sd.InputStream(samplerate=SAMPLERATE, channels=CHANNELS, callback=callback):
            while recording:
                sd.sleep(100)
    except Exception as e:
        print(f"❌ Recording error: {e}")

def transcribe_file(input_file, duration_sec=None):
    print("\n🧠 Transcribing...")
    overall_start = time.time()
    model = WhisperModel("medium", device="cuda", compute_type="float16")
    segments, _ = model.transcribe(
        input_file,
        beam_size=5,
        best_of=5
    )
    raw_text = " ".join([seg.text for seg in segments])

    norm_start = time.time()
    if USE_NORMALIZER and NORMALIZER_AVAILABLE:
        normalized_text = normalizer(raw_text)
    else:
        normalized_text = raw_text
    norm_end = time.time()

    with open(TEXT_FILENAME, "w", encoding="utf-8") as f:
        f.write(normalized_text)

    overall_end = time.time()

    transcript_duration = overall_end - overall_start
    normalization_time = norm_end - norm_start
    text_length = len(normalized_text)
    print("📝 Transcription complete.\n")
    print(normalized_text)
    print("\n📊 Stats:")
    if duration_sec is not None:
        print(f" - Input duration       : {duration_sec:.2f} seconds")
        print(f" - Real-time factor     : {transcript_duration / duration_sec:.2f}x")
    print(f" - Transcription time   : {transcript_duration:.2f} seconds")
    print(f" - Normalization time   : {normalization_time:.4f} seconds")
    print(f" - Output text length   : {text_length} characters")
    print(f" - Saved to             : {TEXT_FILENAME}")

    if USE_NORMALIZER:
        print("\n📋 Comparison:")
        print("Raw transcription:")
        print(raw_text)

    if USE_NORMALIZER and not NORMALIZER_AVAILABLE:
        print("⚠️  Normalizer is enabled but not available. Run:\n  pip install git+https://github.com/openai/whisper.git")

def stop_and_transcribe():
    global recording
    recording = False
    record_end_time = time.time()
    duration_sec = record_end_time - record_start_time
    print(f"\n🛑 Recording stopped. Duration: {duration_sec:.2f} seconds")

    audio_data = np.concatenate(audio_buffer, axis=0)
    sf.write(AUDIO_FILENAME, audio_data, SAMPLERATE)

    transcribe_file(AUDIO_FILENAME, duration_sec)

def handle_exit(signum, frame):
    stop_and_transcribe()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice transcriber using faster-whisper")
    parser.add_argument("--file", type=str, help="Optional input WAV file to transcribe directly")
    args = parser.parse_args()

    if args.file:
        if not os.path.isfile(args.file):
            print(f"❌ File not found: {args.file}")
        else:
            duration = sf.info(args.file).duration
            transcribe_file(args.file, duration_sec=duration)
    else:
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        start_immediate_recording()
