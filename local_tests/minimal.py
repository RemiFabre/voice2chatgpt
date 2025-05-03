from faster_whisper import WhisperModel
import time

model = WhisperModel("medium", device="cuda", compute_type="float16")

start = time.time()
segments, info = model.transcribe("audio.wav")  # Replace with your file
end = time.time()

print("🕒 Transcription time:", round(end - start, 2), "seconds")
print("🌐 Detected language:", info.language)
print("📄 Transcription:")
for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
