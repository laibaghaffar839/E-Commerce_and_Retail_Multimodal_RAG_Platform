from sentence_transformers import SentenceTransformer

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    """
    Convert text into a vector embedding
    """
    embedding = model.encode(text).tolist()

    return embedding
