from pathlib import Path
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")
CHROMA_DIR = Path("storage/chroma")
COLLECTION_NAME = "capstone_documents"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_pdfs():
    documents = []

    for pdf_file in DATA_DIR.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = pdf_file.name

        documents.extend(docs)

    return documents


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=120,
    )

    return splitter.split_documents(documents)


def build_vectorstore(chunks):
    # Start with a clean index so repeated ingestion
    # does not create duplicate documents.
    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    db = Chroma(
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    db.add_documents(chunks)

    return db


if __name__ == "__main__":
    documents = load_pdfs()
    chunks = split_documents(documents)

    print(f"PDF pages loaded : {len(documents)}")
    print(f"Chunks created   : {len(chunks)}")

    db = build_vectorstore(chunks)

    print(f"Chroma documents : {db._collection.count()}")
    print(f"Chroma collection: {COLLECTION_NAME}")
    print(f"Chroma path      : {CHROMA_DIR}")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk.page_content[:500])
        print("Source:", chunk.metadata.get("source"))