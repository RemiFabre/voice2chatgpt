import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

PROMPT = """You are a helpful assistant that cleans up text and suggests filenames.

Given this raw text:
"talked about the redesign of the mercury dashboard we added the upload button and fixed the api bug"

1. Re-punctuate the text correctly.
2. Suggest a filename based on its content.
3. Return both as JSON with fields: 'punctuated_text' and 'suggested_filename'.
"""
# "model": "mistral" (7B) ,"phi",  # or "gemma:2b", etc.
payload = {
    "model": "gemma:2b",
    "prompt": PROMPT,
    "stream": False
}

print("⏳ Sending request to Mistral...")

start_time = time.time()
response = requests.post(OLLAMA_URL, json=payload)
elapsed_time = time.time() - start_time

result = response.json()

print("\n💬 Mistral's Response:\n")
print(result["response"])
print(f"\n⏱️ Response time: {elapsed_time:.2f} seconds")
