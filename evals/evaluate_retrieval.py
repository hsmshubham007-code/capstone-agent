import json
from pathlib import Path

from app.retrieval import search_documents

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATASET_PATH = (
    PROJECT_ROOT
    / "evals"
    / "evaluation_dataset.json"
)

RESULTS_PATH = (
    PROJECT_ROOT
    / "evals"
    / "retrieval_evaluation_results.json"
)


def normalize(value):
    return str(value).lower().strip()


def source_matches(actual_source, expected_sources):
    actual = normalize(actual_source)

    return any(
        normalize(expected) in actual
        or actual in normalize(expected)
        for expected in expected_sources
    )


def evaluate_case(case, k):
    question = case["question"]
    expected_sources = case.get(
        "expected_sources",
        [],
    )

    results = search_documents(
        question,
        k=k,
    )

    retrieved_sources = []

    ranked_results = []

    for rank, (doc, score) in enumerate(
        results,
        start=1,
    ):
        source = doc.metadata.get(
            "source",
            "",
        )

        retrieved_sources.append(source)

        ranked_results.append(
            {
                "rank": rank,
                "source": source,
                "distance": round(
                    float(score),
                    4,
                ),
                "content_preview": (
                    doc.page_content[:300]
                ),
            }
        )

    if expected_sources:
        expected_source_found = any(
            source_matches(
                source,
                expected_sources,
            )
            for source in retrieved_sources
        )
    else:
        expected_source_found = (
            len(retrieved_sources) == 0
        )

    return {
        "id": case["id"],
        "category": case["category"],
        "question": question,
        "expected_sources": expected_sources,
        "retrieved_sources": retrieved_sources,
        "expected_source_found": (
            expected_source_found
        ),
        "results": ranked_results,
    }


def main():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        dataset = json.load(file)

    k_values = [1, 2, 3]

    all_results = {}

    print("=" * 60)
    print("RETRIEVAL-ONLY EVALUATION")
    print("=" * 60)

    for k in k_values:
        print()
        print("=" * 60)
        print(f"TOP-K = {k}")
        print("=" * 60)

        case_results = []

        for case in dataset:
            result = evaluate_case(
                case,
                k,
            )

            case_results.append(result)

            print()
            print(
                f"{result['id']} "
                f"({result['category']})"
            )

            print(
                f"Question: "
                f"{result['question']}"
            )

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
                    f"{item['source']} "
                    f"(distance="
                    f"{item['distance']})"
                )

        in_scope = [
            result
            for result in case_results
            if result["category"]
            != "Out-of-scope"
        ]

        out_of_scope = [
            result
            for result in case_results
            if result["category"]
            == "Out-of-scope"
        ]

        in_scope_success = sum(
            1
            for result in in_scope
            if result["expected_source_found"]
        )

        out_of_scope_clean = sum(
            1
            for result in out_of_scope
            if not result["retrieved_sources"]
        )

        in_scope_rate = (
            in_scope_success
            / len(in_scope)
            if in_scope
            else 0.0
        )

        out_of_scope_rate = (
            out_of_scope_clean
            / len(out_of_scope)
            if out_of_scope
            else 0.0
        )

        all_results[str(k)] = {
            "in_scope_success": (
                in_scope_success
            ),
            "in_scope_total": len(in_scope),
            "in_scope_success_rate": round(
                in_scope_rate,
                4,
            ),
            "out_of_scope_no_evidence": (
                out_of_scope_clean
            ),
            "out_of_scope_total": (
                len(out_of_scope)
            ),
            "out_of_scope_no_evidence_rate": round(
                out_of_scope_rate,
                4,
            ),
            "cases": case_results,
        }

        print()
        print(
            f"Top-{k} in-scope retrieval: "
            f"{in_scope_success}/"
            f"{len(in_scope)} "
            f"({in_scope_rate * 100:.1f}%)"
        )

        print(
            f"Top-{k} out-of-scope clean: "
            f"{out_of_scope_clean}/"
            f"{len(out_of_scope)} "
            f"({out_of_scope_rate * 100:.1f}%)"
        )

    report = {
        "dataset": str(DATASET_PATH),
        "k_values": k_values,
        "results": all_results,
        "configuration": {
            "embedding_model": (
                "sentence-transformers/"
                "all-MiniLM-L6-v2"
            ),
            "chunk_size": 800,
            "chunk_overlap": 150,
            "max_distance": 1.10,
        },
        "limitations": [
            "The evaluation dataset currently contains only five cases.",
            "This benchmark evaluates source retrieval, not answer correctness.",
            "Expected-source matching is based on source metadata.",
            "Retrieval distance is specific to the embedding model and vector store.",
        ],
    }

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
    print("RETRIEVAL EVALUATION COMPLETE")
    print("=" * 60)

    print(
        f"Results saved to: "
        f"{RESULTS_PATH}"
    )


if __name__ == "__main__":
    main()