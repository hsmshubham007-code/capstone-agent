from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "storage/chroma"
COLLECTION_NAME = "capstone_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


_embeddings = None
_db = None


def get_embeddings():
    """
    Create the Hugging Face embedding model lazily.

    The model is not downloaded or initialized when this
    module is imported. It is initialized only when
    document search is actually requested.
    """

    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

    return _embeddings


def get_db():
    """
    Create the Chroma database connection lazily.

    This prevents Hugging Face model initialization during
    pytest collection and application imports.
    """

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
    max_distance=1.4,
):
    """
    Search the company policy documents.

    The embedding model and Chroma database are initialized
    only when this function is actually called.
    """

    db = get_db()

    results = db.similarity_search_with_score(
        query,
        k=k,
    )

    return [
        (doc, score)
        for doc, score in results
        if score <= max_distance
    ]


if __name__ == "__main__":
    query = input("Ask a question: ")

    results = search_documents(query)

    print(f"\nResults found: {len(results)}")

    for i, (doc, score) in enumerate(
        results,
        1,
    ):
        print(f"\n--- Result {i} ---")
        print(f"Score  : {score:.4f}")
        print(
            f"Source : {doc.metadata.get('source')}"
        )
        print(doc.page_content[:500])