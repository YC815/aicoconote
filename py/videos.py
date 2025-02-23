import os
import yt_dlp
import openai
import dotenv

dotenv.load_dotenv()

# 获取用户输入的影片 URL
youtube_url = input("请输入影片网址: ")

# 设置 yt-dlp 选项
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'audio.mp3',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'simulate': True  # 模拟下载，用于检查链接是否受支持
}

# 检查链接是否受支持
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(youtube_url, download=False)
        if result:
            print("该链接受支持，开始下载音频...")
            # 移除 'simulate' 选项以实际下载
            ydl_opts.pop('simulate', None)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
        else:
            print("该链接不受支持。")
except yt_dlp.utils.DownloadError:
    print("该链接不受支持或无法下载。")

# 開啟音訊檔案，送給 OpenAI Whisper API 進行轉錄
with open("audio.mp3.mp3", "rb") as audio_file:
    response = openai.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text"  # 可選："text", "json", "verbose_json", "srt", "vtt"
    )

with open("transcript.txt", "w") as f:
    f.write(response)
# transcription = response["text"]  # Whisper API 直接回傳文本
# print("逐字稿：", transcription)
