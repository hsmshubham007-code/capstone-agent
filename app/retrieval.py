from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DIR = "storage/chroma"
COLLECTION_NAME = "capstone_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

db = Chroma(
    persist_directory=CHROMA_DIR,
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings
)


def search_documents(query, k=3, max_distance=1.4):
    results = db.similarity_search_with_score(query, k=k)

    return [
        (doc, score)
        for doc, score in results
        if score <= max_distance
    ]


if __name__ == "__main__":
    query = input("Ask a question: ")

    results = search_documents(query)

    print(f"\nResults found: {len(results)}")

    for i, (doc, score) in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Score  : {score:.4f}")
        print(f"Source : {doc.metadata.get('source')}")
        print(doc.page_content[:500])