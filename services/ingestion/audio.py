from services.groq_client import client


def extract_audio(file_path: str) -> list[str]:
    """
    Transcribe an audio file using Groq Whisper.
    Returns:
        list[str]: Transcript as a single string.
    """

    with open(file_path, "rb") as audio_file:

        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            response_format="text"
        )

    text = transcription.strip()

    if not text:
        return []

    return [text]