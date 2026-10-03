def extract_txt(file_path: str) -> list[str]:
    """
    Extract text from a TXT file.
    Returns:
        list[str]: Extracted text.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    if not text.strip():
        return []

    return [text]