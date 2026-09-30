import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.ingest import load_pdfs, split_documents

load_dotenv()

CHROMA_DIR = Path("storage/chroma")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)


def create_vectorstore():
    documents = load_pdfs()
    chunks = split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="capstone_documents",
    )

    return vectorstore, len(documents), len(chunks)


if __name__ == "__main__":
    vectorstore, pages, chunks = create_vectorstore()

    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Pages embedded : {pages}")
    print(f"Chunks stored  : {chunks}")
    print(f"Chroma path    : {CHROMA_DIR}")