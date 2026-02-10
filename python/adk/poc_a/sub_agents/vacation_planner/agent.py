from dotenv import load_dotenv
from google.adk import Agent

from shared.model import get_model

load_dotenv()

model = get_model()

vacation_planner = Agent(
    name="vacation_planner",
    model=model,
    description="Vacation planner.",
    instruction="""
    Suggest places to go for vacation. 
    """,
)
