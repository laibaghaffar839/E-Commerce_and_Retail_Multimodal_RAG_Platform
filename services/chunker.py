# Chunk text
def chunk_text(texts: list[str],chunk_size: int = 500,overlap: int = 50) -> list[str]:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    """
    Combine extracted text and split it into overlapping chunks.
    """

    full_text = " ".join(texts)

    words = full_text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start = end - overlap

    return chunks
