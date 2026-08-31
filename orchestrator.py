import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from config import MODEL_NAME
from clarifier_agent import clarifier_agent
from planner_agent import planner_agent
from search_agent import search_agent
from writer_agent import writer_agent, ReportData
from email_agent import email_agent

load_dotenv(override=True)


# ---------- Agents as tools ----------
planner_tool = planner_agent.as_tool(
    tool_name="plan_searches",
    tool_description=(
        "Takes the research query. Returns a list of web search terms, each with a reason. "
        "Call this once, first."
    ),
)

search_tool = search_agent.as_tool(
    tool_name="search",
    tool_description=(
        "Searches the web for ONE search term and returns a short summary. "
        "Input format: 'Search term: <term>\nReason for searching: <reason>'. "
        "Call once per term in the plan."
    ),
)

writer_tool = writer_agent.as_tool(
    tool_name="write_report",
    tool_description=(
        "Writes the final report. Input must contain the original query AND all search "
        "summaries collected so far. Call once, after all searches are done."
    ),
)

email_tool = email_agent.as_tool(
    tool_name="send_email",
    tool_description=(
        "Sends the finished report by email. Input is the full markdown report. "
        "Call exactly once, at the very end, after write_report."
    ),
)


# ---------- Manager ----------
MANAGER_INSTRUCTIONS = """
You are a research manager. You produce a researched report by using your tools in order.

Follow these steps exactly:
1. Call plan_searches once with the user's query. It returns a list of search terms.
2. For EACH term in that plan, call search once. Do not skip terms and do not combine
   several terms into one call. Keep every summary you get back.
3. Call write_report once, passing the original user query together with all the
   summaries from step 2.
4. Call send_email once with the markdown report from step 3.

Then reply with the full markdown report as your final answer.

If a search fails, continue with the remaining terms rather than stopping.
"""

manager_agent = Agent(
    name="manager_agent",
    instructions=MANAGER_INSTRUCTIONS,
    tools=[planner_tool, search_tool, writer_tool, email_tool],
    model=MODEL_NAME,
)


# ---------- Clarification (stays outside the manager) ----------
async def get_clarifying_questions(query: str) -> list[str]:
    result = await Runner.run(clarifier_agent, query)
    return result.final_output.questions


def build_enriched_query(query: str, questions: list[str], answers: str) -> str:
    if not questions or not answers.strip():
        return query

    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))

    return f"""Original query: {query}

The user was asked these clarifying questions:
{numbered}

The user's answers (freeform, may not map one-to-one to the questions):
{answers.strip()}"""


# ---------- Entry point ----------
async def main(query: str) -> str:
    with trace("Deep research (manager)"):
        result = await Runner.run(manager_agent, query, max_turns=30)
    return result.final_output


if __name__ == "__main__":
    task = "Most popular AI Agent frameworks in 2026"
    print(asyncio.run(main(task)))