import os
import tempfile

from moviepy import VideoFileClip
from services.ingestion.audio import extract_audio


def extract_video(file_path: str) -> list[str]:
    """
    Extract audio from a video and transcribe it.
    Returns:
        list[str]
    """

    with tempfile.NamedTemporaryFile(suffix=".mp3",delete=False) as temp_audio:
        audio_path = temp_audio.name

    try:

        video = VideoFileClip(file_path)
        video.audio.write_audiofile(
            audio_path,
            logger=None
        )

        video.close()
        return extract_audio(audio_path)

    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)