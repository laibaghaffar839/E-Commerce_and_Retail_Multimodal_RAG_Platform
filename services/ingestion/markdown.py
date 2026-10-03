def extract_md(file_path: str) -> list[str]:
    """
    Extract text from a Markdown file.
    Returns:
        list[str]: Markdown content.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    if not text.strip():
        return []

    return [text]