import logging
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from google.genai.types import Content

from shared.callbacks import display_agent_state
from shared.model import get_model
from .constants import Field
from .sub_agents.solution_architecture_team import solution_architecture_team
from .tools import set_state_tool, load_file_data_into_state_tool

logging.basicConfig(level=logging.INFO)

load_dotenv()

model = get_model()


def inject_state(callback_context: CallbackContext) -> Optional[Content]:
    callback_context.state.update({
        "timestamp": datetime.now().strftime('%Y%m%d%H%M'),
    })


root_agent = Agent(
    name="root_agent",
    model=model,
    description="Guides the user in creating an architecture design and solution.",
    instruction=f"""
    ROLE:
    You are a helpful engineering solution coordinator.

    # INSTRUCTIONS:
    1. Ask the user for filename (ex: filename.txt) to load from 'problems' directory.
    2. Use 'set_state_tool' to save the filename into the {Field.PROBLEM_FILENAME} field.
    3. Use 'load_file_data_into_state_tool' to load the file from the 'problems' directory into the {Field.PROBLEM} field.
    4. Ask the user if they wish to proceed with solution design.
    5. If the user agrees, confirm your support and hand off to the solution_architecture_team.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        set_state_tool,
        load_file_data_into_state_tool,
    ],
    sub_agents=[solution_architecture_team],
    before_agent_callback=inject_state,
    after_agent_callback=display_agent_state,
)
