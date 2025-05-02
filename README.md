# Voice Transcriber (Whisper + Hotkey)

This project turns your computer into a hotkey-triggered voice transcriber powered by Whisper. It captures your speech with a single keyboard shortcut, transcribes it locally using Whisper (via Faster-Whisper), and displays the result in the terminal. It's designed to work fully offline and fast.

## Features

* Hotkey-triggered recording
* Local Whisper transcription (via Faster-Whisper)
* Real-time mic level bar in terminal
* Optionally normalize text

---

## 🔧 Installation (Linux)

### 1. Clone the repo

```bash
git clone git@github.com:RemiFabre/voice2chatgpt.git
cd voice2chatgpt
```

### 2. Create and activate virtual environment

```bash
python3 -m venv ~/.virtualenvs/whisper
source ~/.virtualenvs/whisper/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# or, manually:
pip install faster-whisper sounddevice soundfile numpy pynput
```

> ⚠️ Optional: If you want to enable normalization (not that useful):

```bash
pip install git+https://github.com/openai/whisper.git
```

---

## 🎙️ Running the tool manually

From inside your virtualenv:

```bash
python voice_transcriber.py
```

Then just talk. Press `Ctrl+C` to stop and get the transcript.

You can also transcribe an existing `.wav` file:

```bash
python voice_transcriber.py --file your_audio.wav
```

---

## ⌨️ Set up a global hotkey (Ubuntu/Linux)

### 1. Create a shell launcher

Modify `run_transcriber.sh` to fit your path.

Make it executable:

```bash
chmod +x ~/voice2chatgpt/run_transcriber.sh
```

### 2. (optional) Create a desktop shortcut

Create the file:

```bash
~/.local/share/applications/voice-transcriber.desktop
```

With content (adapt Exec path):

```ini
[Desktop Entry]
Type=Application
Name=Voice Transcriber
Exec=/home/remi/voice2chatgpt/run_transcriber.sh
Icon=utilities-terminal
Terminal=true
```

Then update your local desktop database:

```bash
update-desktop-database ~/.local/share/applications
```

### 3. Bind the shortcut

Go to:

```
Settings → Keyboard → Custom Shortcuts
```

Add (adapt command path):

* Name: `Voice Transcriber`
* Command: `/home/remi/voice2chatgpt/run_transcriber.sh`
* Shortcut: for example, `Ctrl+Alt+Space`

---

## 🛠️ Configurable options

In `voice_transcriber.py`:

* `USE_NORMALIZER`: Set to `True` to clean punctuation and casing
* `SAMPLERATE`, `CHANNELS`: Customize recording fidelity
* `BAR_WIDTH`: Width of the real-time mic bar

---

## 🧪 Notes

* Output is saved in `transcription.txt`
* Input audio is saved as `recorded.wav`
* Uses Whisper's `medium` model by default (can be changed in code)
* Real-time factor is printed to evaluate performance

---

## 🧼 .gitignore recommendation

Include `*.wav`, `*.txt`, and `voice_log.txt` to avoid cluttering the repo.

---

## ✅ Tested With

* Ubuntu 22.04 LTS
* Python 3.10
* NVIDIA GPU (CUDA-accelerated Faster-Whisper)
* Terminal: Terminator or Gnome Terminal

---

## License

MIT
