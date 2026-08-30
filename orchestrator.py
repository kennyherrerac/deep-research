from dotenv import load_dotenv
from agents import Runner, trace
import asyncio

# Agents
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent

# --- Import of env variables
load_dotenv(override=True)


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


if __name__ == "__main__":
    task = "Most popular AI Agent frameworks in 2026"
    final_report = asyncio.run(main(task))
    print(final_report.markdown_report)