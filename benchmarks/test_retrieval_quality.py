from app.retrieval import search_documents

QUESTIONS = [
    "What does the policy say about employee benefits?",
    "What is the company's policy on workplace harassment?",
    "What are the rules regarding employee conduct?",
    "What does the policy say about working hours?",
    "What is the policy for taking time off?",
    "What is the company's mission?",
    "What are the company's rules for confidential information?",
    "What does the company policy say about conflicts of interest?",
    "What are the rules for intellectual property?",
    "What does the company require for ethical business practices?",
    "Who is allowed to make official public statements for the company?",
    "What is the company's password policy?",
    "What are the rules for protecting company devices?",
    "What does the IT policy say about access control?",
    "What are the rules for handling company data?",
    "What should employees do if they suspect a security incident?",
    "What does the company policy say about information security?",
]


for question in QUESTIONS:
    print()
    print("=" * 90)
    print("QUESTION:", question)
    print("=" * 90)

    results = search_documents(question)

    print("RESULTS:", len(results))

    for doc, score in results:
        source = doc.metadata.get("source")

        text = (
            doc.page_content
            .replace("\n", " ")
            [:250]
        )

        print()
        print(
            f"SOURCE: {source}"
        )

        print(
            f"SCORE: {float(score):.4f}"
        )

        print(
            f"TEXT: {text}"
        )