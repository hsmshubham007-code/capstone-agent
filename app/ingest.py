from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


DATA_DIR = Path("data")


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
        chunk_overlap=120
    )

    return splitter.split_documents(documents)


if __name__ == "__main__":
    documents = load_pdfs()
    chunks = split_documents(documents)

    print(f"PDF pages loaded : {len(documents)}")
    print(f"Chunks created   : {len(chunks)}")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(chunk.page_content[:500])
        print("Source:", chunk.metadata.get("source"))