import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.context import build_contextual_query

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = os.getenv("GROQ_MODEL")


def decide_tool(question, history=None):
    history = history or []

    contextual_question = build_contextual_query(
        question,
        history
    )

    prompt = f"""
You are an agent router.

Choose the correct action for the user question.

Available actions:
- search_documents: use this for questions about company policies, employees, workplace rules, IT policies, HR policies, or information that may exist in company documents.
- no_tool: use this when the question clearly cannot be answered using company documents.

Important:
- Follow-up questions refer to the previous conversation.
- If the current question is a follow-up to a company-document question, choose search_documents.
- "Tell me that again", "what about that?", "explain more", and similar follow-ups should use the same tool as the previous relevant question.

Return ONLY valid JSON.

Format:
{{"tool": "search_documents"}}

or:

{{"tool": "no_tool"}}

Conversation:
{contextual_question}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    content = response.choices[0].message.content

    return json.loads(content)["tool"]