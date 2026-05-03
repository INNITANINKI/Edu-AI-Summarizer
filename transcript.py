import os
import re
import yt_dlp
from faster_whisper import WhisperModel
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str):
    """Extract YouTube video ID from URL."""
    url = re.sub(r'([&?]t=\d+[smh]?)', '', url)
    m = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return m.group(1) if m else None


def fetch_transcript(video_id: str, out_dir: str = "temp") -> str:
    """Fetch transcript using YouTubeTranscriptApi or fallback to Whisper."""
    # Try YouTubeTranscriptApi
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([t['text'] for t in transcript_list])
        if transcript_text.strip():
            print("✅ Transcript fetched via YouTubeTranscriptApi.")
            return transcript_text
    except Exception:
        print("⚠️ YouTubeTranscriptApi failed. Falling back to Whisper...")

    # Download audio
    os.makedirs(out_dir, exist_ok=True)
    audio_path = os.path.join(out_dir, f"{video_id}.%(ext)s").replace("\\", "/")
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": audio_path,
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        audio_file = os.path.join(out_dir, f"{video_id}.mp3")
        if not os.path.exists(audio_file):
            print(f"❌ Audio download failed: file not found {audio_file}")
            return ""
        print(f"📥 Audio downloaded: {audio_file}")
    except Exception as e:
        print(f"❌ Failed to download audio: {e}")
        return ""

    # Transcribe with Whisper
    try:
        model_size = "tiny"
        device = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print(f"🎙 Transcribing with faster-whisper ({model_size}, {device}, {compute_type})...")
        segments, _ = model.transcribe(audio_file)
        transcript_text = " ".join([seg.text for seg in segments])
        print("✅ Whisper transcription complete.")
        return transcript_text.strip()
    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return ""