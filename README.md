# voice2chatgpt (Whisper + Hotkey + ChatGPT)

This project turns your computer into a hotkey-triggered voice transcriber powered by Whisper. It captures your speech with a single keyboard shortcut, transcribes it locally using Whisper (via Faster-Whisper), and displays the result in the terminal or sends it to ChatGPT. It's designed to work fully offline and fast.

## Features

* Hotkey-triggered recording
* Local Whisper transcription (via Faster-Whisper)
* Real-time mic level bar in terminal + live duration
* Press keys `1`–`5` during or after recording to choose what to do:
  * `1` – Show transcription
  * `2` – Send to ChatGPT (opens Firefox, pastes & submits)
  * `3` – Copy to clipboard
  * `4` – Save and exit
  * `5` – Cancel and discard
* Live keypress debug display (shows unknown key codes)
* Compatible with QWERTY, AZERTY, and numpad layouts
* Optionally normalize text (punctuation & casing)

---

## 🔧 Installation (Linux)

### 1. Clone the repo

```bash
git clone git@github.com:RemiFabre/voice2chatgpt.git
cd voice2chatgpt
````

### 2. Create and activate virtual environment

```bash
python3 -m venv ~/.virtualenvs/whisper
source ~/.virtualenvs/whisper/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
# or, manually:
pip install faster-whisper sounddevice soundfile numpy pynput pyperclip pyautogui
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

Then just talk. The script will show your mic level and elapsed time.
Press `1`–`5` *during* or *after* the recording to:

* Show transcription
* Send it to ChatGPT (in Firefox)
* Copy to clipboard
* Save
* Cancel

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

* `MODEL_SIZE`: Change from `"medium"` to `"small"` for faster speed
* `USE_NORMALIZER`: Set to `True` to clean punctuation and casing
* `SAMPLE_RATE`, `CHANNELS`: Customize recording fidelity
* `MIC_BAR_WIDTH`: Width of the real-time mic bar

---

## 🧪 Notes

* Output is saved in `transcription.txt`
* Input audio is saved as `recorded.wav`
* Works even offline (if models are pre-cached)
* Prints real-time factor and durations
* On unknown keyboard layouts, raw key codes like `<65437>` are printed — you can add support easily by extending `key_map`

---

## 🧼 .gitignore recommendation

Include:

```
*.wav
*.txt
voice_log.txt
```

---

## ✅ Tested With

* Ubuntu 22.04 LTS
* Python 3.10
* NVIDIA GPU (CUDA-accelerated Faster-Whisper)
* AZERTY & QWERTY keyboard layouts
* Firefox (for ChatGPT integration)
* Terminal: Terminator or Gnome Terminal

---

## License

MIT
