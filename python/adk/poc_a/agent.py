from dotenv import load_dotenv
from google.adk import Agent

from .sub_agents.vacation_planner import vacation_planner
from shared.model import get_model

load_dotenv()

model = get_model()

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction="""
    If the user ask for vacation suggestions, handoff to vacation_planner to get attraction suggestions.
    """,
    sub_agents=[vacation_planner],
)
