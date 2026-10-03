import base64
from services.groq_client import client


def extract_image(file_path: str) -> list[str]:
    """
    Analyze an image using Groq vision model.
    Returns image understanding as text.
    """

    with open(file_path, "rb") as image_file:
        image_bytes = image_file.read()

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze this image and extract all useful information from it. Return the result as clear text for RAG."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        temperature=0,
        max_tokens=800
    )

    text = response.choices[0].message.content.strip()

    if not text:
        return []

    return [text]