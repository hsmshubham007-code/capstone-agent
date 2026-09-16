from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "storage/chroma"
COLLECTION_NAME = "capstone_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Lower distance = more similar.
# This is intentionally stricter than the previous 1.4 threshold.
DEFAULT_MAX_DISTANCE = 1.10

_embeddings = None
_db = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

    return _embeddings


def get_db():
    global _db

    if _db is None:
        _db = Chroma(
            persist_directory=CHROMA_DIR,
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
        )

    return _db


def search_documents(
    query,
    k=3,
    max_distance=DEFAULT_MAX_DISTANCE,
):
    """
    Search company documents and keep only sufficiently
    similar results.

    Chroma returns a distance score where:
        lower = more similar
        higher = less similar
    """

    db = get_db()

    results = db.similarity_search_with_score(
        query,
        k=k,
    )

    filtered_results = [
        (doc, score)
        for doc, score in results
        if score <= max_distance
    ]

    return filtered_results