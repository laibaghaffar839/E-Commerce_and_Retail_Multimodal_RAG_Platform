from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid


# Initialize Qdrant client
client = QdrantClient(":memory:")


# Collection name
COLLECTION_NAME = "multimodal_documents"


# Create collection
def create_collection():
    collections = client.get_collections().collections

    collection_names = [collection.name for collection in collections]

    if COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

# Store document chunks and their embeddings

def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    room_id: int,
    file_id: int,
    filename: str,
    file_type: str
):

    points = []

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        point = PointStruct(
            id=str(uuid.uuid4()),

            vector=embedding,

            payload={
                "text": chunk,
                "room_id": room_id,
                "file_id": file_id,
                "filename": filename,
                "chunk_index": index,
                "file_type": file_type
            }
        )

        points.append(point)


    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )