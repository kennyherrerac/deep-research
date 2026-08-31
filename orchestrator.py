from dotenv import load_dotenv
from agents import Runner, trace
import asyncio

# Agents
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
from clarifier_agent import clarifier_agent

# --- Import of env variables
load_dotenv(override=True)


async def get_clarifying_questions(query: str) -> list[str]:
    print("Clarifying the query...")
    result = await Runner.run(clarifier_agent, query)
    return result.final_output.questions


async def plan_searches(query: str) -> WebSearchPlan:
    print("Planning searches...")
    result = await Runner.run(planner_agent, query)
    plan = result.final_output
    print(f"Will do {len(plan.searches)} searches")
    return plan


async def search(item: WebSearchItem) -> str | None:
    input_message = f"Search term: {item.query}\nReason for searching: {item.reason}"
    try:
        result = await Runner.run(search_agent, input_message)
        return result.final_output
    except Exception as exc:
        print(f"Search failed for '{item.query}': {exc}")
        return None


async def perform_searches(plan: WebSearchPlan) -> list[str]:
    tasks = [asyncio.create_task(search(item)) for item in plan.searches]
    results = [r for r in await asyncio.gather(*tasks) if r is not None]
    print(f"Finished searching, {len(results)}/{len(plan.searches)} succeeded")
    return results


async def write_report(query: str, search_results: list[str]) -> ReportData:
    print("Thinking about report...")
    input_message = f"Original query: {query}\nSummarized search results: {search_results}"
    result = await Runner.run(writer_agent, input_message)
    print("Finished writing report")
    return result.final_output


async def send_report_email(report: ReportData) -> None:
    print("Writing email...")
    await Runner.run(email_agent, report.markdown_report)
    print("Email sent")


async def main(task: str) -> ReportData:
    with trace("Deep research trace"):
        plan = await plan_searches(task)
        search_results = await perform_searches(plan)
        report = await write_report(task, search_results)
        await send_report_email(report)
    return report

def build_enriched_query(query: str, questions: list[str], answers: str) -> str:
    if not questions or not answers.strip():
        return query

    numbered = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))

    return f"""Original query: {query}

            The user was asked these clarifying questions:
            {numbered}

            The user's answers (freeform, may not map one-to-one to the questions):
            {answers.strip()}"""
        
        

async def cli_run(task: str, answers: str) -> ReportData:
    questions = await get_clarifying_questions(task)
    print("Questions:", questions)
    enriched = build_enriched_query(task, questions, answers)
    return await main(enriched)


if __name__ == "__main__":
    task = "Most commercially successful implementation of MCP and Agents in ERP, CRM and salesforce data"
    answers = "Model Context Protocol. Salesforce the platform. Global, last 2 years."
    report = asyncio.run(cli_run(task, answers))
    print(report.markdown_report)
