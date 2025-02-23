import os
import yt_dlp
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import dotenv

dotenv.load_dotenv()

# YouTube 影片 URL
youtube_url = "https://www.youtube.com/watch?v=T1jds1GuVXg"

# 下載音訊
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio.mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([youtube_url])

# 開啟音訊檔案，送給 OpenAI Whisper API 進行轉錄
with open("audio.mp3", "rb") as audio_file:
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"  # 可選："text", "json", "verbose_json", "srt", "vtt"
    )

transcription = response  # Whisper API 直接回傳文本
print("逐字稿：", transcription)

# 進一步讓 GPT-4 摘要重點
summary_response = client.chat.completions.create(model="gpt-4",
messages=[
    {"role": "system", "content": "請擷取這段內容的重點摘要"},
    {"role": "user", "content": transcription}
])

summary = summary_response.choices[0].message.content
print("重點摘要：", summary)
with open("summary.txt", "w") as f:
    f.write(summary)
