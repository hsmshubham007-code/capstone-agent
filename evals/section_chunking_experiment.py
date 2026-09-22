import json
import re
import shutil
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
EXPERIMENT_DIR = PROJECT_ROOT / "storage" / "chroma_section_test"

COLLECTION_NAME = "section_chunk_test"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DATASET_PATH = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_dataset.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "evals"
    / "section_chunking_results.json"
)


def load_policy_sections(pdf_path):
    reader = PdfReader(str(pdf_path))

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    heading_pattern = re.compile(
        r"(?m)^\s*(\d+)\.\s+(.+?)\s*$"
    )

    matches = list(
        heading_pattern.finditer(text)
    )

    sections = []

    for index, match in enumerate(matches):
        section_number = match.group(1)
        section_title = match.group(2).strip()

        start = match.start()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )

        content = text[start:end].strip()

        if not content:
            continue

        sections.append(
            Document(
                page_content=content,
                metadata={
                    "source": pdf_path.name,
                    "section_number": section_number,
                    "section_title": section_title,
                },
            )
        )

    return sections


def build_section_documents():
    documents = []

    for pdf_path in sorted(
        DATA_DIR.glob("*.pdf")
    ):
        sections = load_policy_sections(
            pdf_path
        )

        documents.extend(sections)

    return documents


def source_matches(
    actual_source,
    expected_sources,
):
    actual = str(actual_source).lower().strip()

    return any(
        str(expected).lower().strip() in actual
        or actual
        in str(expected).lower().strip()
        for expected in expected_sources
    )


def evaluate_case(
    db,
    case,
    k,
):
    results = db.similarity_search_with_score(
        case["question"],
        k=k,
    )

    retrieved_sources = [
        doc.metadata.get("source", "")
        for doc, _ in results
    ]

    if case["expected_sources"]:
        expected_source_found = any(
            source_matches(
                source,
                case["expected_sources"],
            )
            for source in retrieved_sources
        )
    else:
        expected_source_found = (
            len(retrieved_sources) == 0
        )

    ranked_results = []

    for rank, (doc, score) in enumerate(
        results,
        start=1,
    ):
        ranked_results.append(
            {
                "rank": rank,
                "source": doc.metadata.get(
                    "source",
                    "",
                ),
                "section_number": doc.metadata.get(
                    "section_number",
                    "",
                ),
                "section_title": doc.metadata.get(
                    "section_title",
                    "",
                ),
                "distance": round(
                    float(score),
                    4,
                ),
            }
        )

    return {
        "id": case["id"],
        "category": case["category"],
        "question": case["question"],
        "expected_sources": case[
            "expected_sources"
        ],
        "retrieved_sources": retrieved_sources,
        "expected_source_found": (
            expected_source_found
        ),
        "results": ranked_results,
    }


def main():
    print("=" * 60)
    print("SECTION-AWARE CHUNKING EXPERIMENT")
    print("=" * 60)

    if EXPERIMENT_DIR.exists():
        shutil.rmtree(EXPERIMENT_DIR)

    documents = build_section_documents()

    print()
    print(
        f"Section chunks created: "
        f"{len(documents)}"
    )

    for document in documents:
        print(
            f"{document.metadata['source']} - "
            f"{document.metadata['section_number']}. "
            f"{document.metadata['section_title']}"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    db = Chroma(
        persist_directory=str(EXPERIMENT_DIR),
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
    )

    db.add_documents(documents)

    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    k_values = [1, 2, 3]

    report = {
        "configuration": {
            "embedding_model": EMBEDDING_MODEL,
            "chunking": "numbered policy sections",
            "collection": COLLECTION_NAME,
        },
        "results": {},
    }

    for k in k_values:
        print()
        print("=" * 60)
        print(f"TOP-K = {k}")
        print("=" * 60)

        cases = []

        for case in dataset:
            result = evaluate_case(
                db,
                case,
                k,
            )

            cases.append(result)

            print()
            print(result["id"])
            print(
                f"Expected: "
                f"{result['expected_sources']}"
            )
            print(
                f"Retrieved: "
                f"{result['retrieved_sources']}"
            )
            print(
                f"Expected source found: "
                f"{result['expected_source_found']}"
            )

            for item in result["results"]:
                print(
                    f"  Rank {item['rank']}: "
                    f"{item['source']} - "
                    f"{item['section_number']}. "
                    f"{item['section_title']} "
                    f"(distance="
                    f"{item['distance']})"
                )

        in_scope = [
            case
            for case in cases
            if case["category"]
            != "Out-of-scope"
        ]

        out_of_scope = [
            case
            for case in cases
            if case["category"]
            == "Out-of-scope"
        ]

        in_scope_success = sum(
            case["expected_source_found"]
            for case in in_scope
        )

        out_of_scope_clean = sum(
            not case["retrieved_sources"]
            for case in out_of_scope
        )

        report["results"][str(k)] = {
            "in_scope_success": (
                in_scope_success
            ),
            "in_scope_total": len(in_scope),
            "in_scope_rate": (
                in_scope_success
                / len(in_scope)
                if in_scope
                else 0
            ),
            "out_of_scope_clean": (
                out_of_scope_clean
            ),
            "out_of_scope_total": (
                len(out_of_scope)
            ),
            "out_of_scope_rate": (
                out_of_scope_clean
                / len(out_of_scope)
                if out_of_scope
                else 0
            ),
            "cases": cases,
        }

        print()
        print(
            f"Top-{k} in-scope retrieval: "
            f"{in_scope_success}/"
            f"{len(in_scope)} "
            f"({100 * report['results'][str(k)]['in_scope_rate']:.1f}%)"
        )

        print(
            f"Top-{k} out-of-scope clean: "
            f"{out_of_scope_clean}/"
            f"{len(out_of_scope)} "
            f"({100 * report['results'][str(k)]['out_of_scope_rate']:.1f}%)"
        )

    with open(
        RESULTS_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    print(
        f"Results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()