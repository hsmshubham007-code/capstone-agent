from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


CHROMA_DIR = "storage/chroma"
COLLECTION_NAME = "capstone_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

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


def expand_query(query: str) -> str:
    """
    Add a small number of domain-specific synonyms for known
    company-policy concepts.

    This improves retrieval for natural-language questions whose
    wording differs from the policy wording.
    """

    query_lower = query.lower()

    expansions = []

    if "working hours" in query_lower:
        expansions.extend(
            [
                "working hours",
                "agreed working hours",
                "attendance",
                "report to work on time",
            ]
        )

    if "time off" in query_lower:
        expansions.extend(
            [
                "time off",
                "leave",
                "planned absence",
                "emergency leave",
            ]
        )

    if "mission" in query_lower:
        expansions.extend(
            [
                "mission",
                "purpose",
                "company purpose",
                "corporate policy purpose",
            ]
        )

    if "company data" in query_lower:
        expansions.extend(
            [
                "company data",
                "data protection",
                "protect company information",
                "information security",
            ]
        )

    if not expansions:
        return query

    return query + " " + " ".join(expansions)


def search_documents(query, k=3, max_distance=DEFAULT_MAX_DISTANCE):
    db = get_db()

    expanded_query = expand_query(query)

    results = db.similarity_search_with_score(
        expanded_query,
        k=k,
    )

    filtered_results = [
        (doc, score)
        for doc, score in results
        if score <= max_distance
    ]

    return filtered_results