# 🎙️ voice2chatgpt

**voice2chatgpt** is a voice-to-text transcription and interaction assistant powered by Whisper and optionally a local LLM (like `gemma:2b` via Ollama). It copies transcriptions to the clipboard and can optionally interact with ChatGPT.

## ✨ Features

- Live voice recording + real-time microphone level bar
- Accurate transcription using `faster-whisper`
- Clipboard copy automatically
- Mode 2: paste into existing ChatGPT tab
- Mode 3: open a new ChatGPT tab and paste
- Mode 4: optionally use a local LLM to:
  - enhance punctuation
  - suggest a smart filename
  - rename the recording folder
- All recordings saved by default in: `recordings/YYYY-MM-DD/HH-MM-SS/`
- Compatible with CUDA GPUs (⚠️ requires enough VRAM)

---

## 🧪 Example

```bash
python3 voice_transcriber.py
````

You’ll see a mic bar, press a key 1–5 during recording:

* `1`: Show result (default)
* `2`: Paste into current ChatGPT tab (requires ChatGPT open)
* `3`: Open ChatGPT and paste there
* `4`: Enhance and rename with local LLM (work in progress)
* `5`: Cancel (discard)

📋 Transcription is always copied to clipboard automatically.

---

## 🖥️ Installation (Minimal Clean Environment)

### 1. Clone the repo

```bash
git clone https://github.com/RemiFabre/voice2chatgpt
cd voice2chatgpt
```

### 2. Create a clean Python virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install extra system tools (Ubuntu)

```bash
sudo apt install ffmpeg xdotool
```

---

## 🧠 Optional: Enable local LLM (for mode 4)

### 1. Install Ollama

Follow instructions at [https://ollama.com](https://ollama.com) to install and run the `ollama` server locally.

### 2. Download your model (recommended: `gemma:2b`)

```bash
ollama run gemma:2b
```

### 3. Leave the server running

Run this in another terminal:

```bash
ollama serve
```

---

## ⚠️ GPU Memory Notes

Whisper (`medium`) and `gemma:2b` **both require GPU memory**. If you get CUDA out-of-memory errors, consider:

* using Whisper in `cpu` mode
* using smaller LLMs
* disabling mode 4 (local LLM)

---

## 🎧 Sounds

This script uses WAV files (`sounds/plop.wav`) for feedback. Replace them with your own short audio cues if needed.

---

## 📦 Directory Structure

Each recording goes in:

```
recordings/YYYY-MM-DD/HH-MM-SS/ 
├── audio.wav
└── transcript.txt
```

If mode 4 is used, the folder is renamed to include the smart name.

---

## 📝 requirements.txt

Basic Python dependencies (already included):

```
sounddevice
soundfile
numpy
pyautogui
pyperclip
faster-whisper
playsound
pynput
requests
```

You can regenerate a clean one via:

```bash
pip freeze > requirements.txt
```

---

## 🔄 Reset

To delete all recordings:

```bash
rm -rf recordings/
```
