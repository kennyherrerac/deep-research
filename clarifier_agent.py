from pydantic import BaseModel, Field
from agents import Agent, Runner
from config import MODEL_NAME
import asyncio
from dotenv import load_dotenv
load_dotenv(override=True)


class ClarifyingQuestions(BaseModel):
    questions: list[str] = Field(description="Up to three questions to ask the user. Empty if the query is already specific enough")


INSTRUCTIONS = """
You are a research assistant. Given a research query, decide whether you need
clarification from the user before searching.

Ask a question only if a different answer would lead you to search for different
things. Typical reasons: an ambiguous term with more than one common meaning, an
unstated scope (region, time period, industry), or an unclear intended use that
changes what evidence matters.

Do not ask about anything the query already specifies. Do not ask generic questions
like "what is your goal" — the user cannot answer those usefully.

Ask at most 3 questions. Ask fewer, or none at all, when the query is already
specific enough to search well. Each question must be answerable in a sentence.
"""

clarifier_agent = Agent(
    name="clasifier-agent",
    instructions=INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ClarifyingQuestions,
)

query = "AI Agents 2026"

async def get_clarifying_questions(query: str) -> list[str]:
    print("Clarifying the query...")
    result = await Runner.run(clarifier_agent, query)
    return result.final_output.questions