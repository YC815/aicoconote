from dotenv import load_dotenv
import re
import json
import requests
import os
import yt_dlp
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

target_language = "Traditional Chinese"

# Prompt user to input video URL
video_url = input("Please enter the video URL: ")

# yt-dlp configuration options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio.%(ext)s',  # Use appropriate output template
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Download audio
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])

audio_file_path = "audio.mp3"
if not os.path.exists(audio_file_path):
    print("Audio file download failed.")
    exit(1)

# Transcribe audio using OpenAI Whisper API
with open(audio_file_path, "rb") as audio_file:
    transcript_response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"
    )

transcript = transcript_response
print("Transcript:", transcript)

# Summarize the transcript using DeepSeek model
api_url = "http://127.0.0.1:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}

messages = [
    {"role": "system", "content": """
        1. Please provide a detailed summary of the following information in Markdown bullet-point format.
        2. Respond strictly in English; deviations will be penalized.
        3. Ensure the output has a clear and logical structure.
        4. Utilize emojis as title icons to enhance readability where appropriate.
        5. For technical terms, include the original term in parentheses after the translation, unless unnecessary.
        6. Reflect thoroughly to avoid hallucinations and cognitive errors.
    """},
    {"role": "user", "content": transcript}
]

data = {"model": "deepseek-r1-distill-qwen-7b", "messages": messages, "temperature": 0.7}
response = requests.post(api_url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    result = response.json()
    english_summary = result["choices"][0]["message"]["content"]
    print("English Summary:", english_summary)
else:
    print("Request failed with status code:", response.status_code)
    exit(1)

# Step 2: Translate English summary to target language using GPT-4
messages = [
    {"role": "system", "content": f"""
        1. Translate the following text into {target_language}.
        2. Preserve the original formatting exactly; do not make any alterations.
    """},
    {"role": "user", "content": english_summary}
]

data = {"model": "gpt-4", "messages": messages, "temperature": 0.7}
response = client.chat.completions.create(**data)

if response:
    translated_summary = response.choices[0].message.content
    print(f"{target_language} Summary:", translated_summary)
else:
    print("Translation request failed.")
