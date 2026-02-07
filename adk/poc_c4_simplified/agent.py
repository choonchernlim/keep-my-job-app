import logging
import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.models import LiteLlm
from google.genai import types

from .tools import set_c4_field_to_state_tool, get_next_c4_from_state_tool

load_dotenv()

model = LiteLlm(model=os.getenv("MODEL")) if os.getenv("LITELLM") else os.getenv("MODEL")
logging.info(model)

c4_content_analyzer = Agent(
    name="c4_content_analyzer",
    model=model,
    description="Set C4 states.",
    instruction="""
    Use 'set_c4_field_to_state_tool' to save the following info into the state:
        - key = 1, field = diagram_type, value = context
        - key = 1, field = description, value = this is my context
        - key = 2, field = diagram_type, value = container
        - key = 2, field = description, value = this is container 1
        - key = 3, field = diagram_type, value = container
        - key = 3, field = description, value = this is container 2
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        set_c4_field_to_state_tool,
    ],
)

c4_syntax = Agent(
    name="c4_syntax",
    model=model,
    description="Generate mermaid syntax for C4 diagrams.",
    instruction="""
    1. Call 'get_next_c4_from_state_tool' with missing_field = mermaid_png_path.
    2. If there is such object:
        - Inform that you will generate the mermaid syntax for the object, example:
            - Template: "Generating C4 syntax (type = [diagram_type], description = [description])...".
            - Example: "Generating C4 syntax (type = container, description = ADO pipeline flow)...".
        - Generate the mermaid syntax based on the diagram_type and description.
        - Use 'set_c4_field_to_state_tool' to save the mermaid syntax back to the state:
            - mermaid_syntax = "this is test"
    3. Repeat until there is no object without mermaid_syntax.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        get_next_c4_from_state_tool,
        set_c4_field_to_state_tool,
    ],
)

c4_writer = Agent(
    name="c4_writer",
    model=model,
    description="Generate mermaid image.",
    instruction="""
    1. Call 'get_next_c4_from_state_tool' to find object with missing mermaid_png_path field.
    2. If there is such object:
        - Inform that you will generate the mermaid image for the object, example:
            - Template: "Generating C4 image (type = [diagram_type], description = [description])...".
            - Example: "Generating C4 image (type = container, description = ADO pipeline flow)...".
        - Generate the mermaid PNG file based on the mermaid_syntax.
        - Use 'set_c4_field_to_state_tool' to save the mermaid syntax back to the state:
            - mermaid_png_path = "/path/to/png"
    3. Repeat until there is no object without mermaid_png_path.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        get_next_c4_from_state_tool,
        set_c4_field_to_state_tool,
    ],
)

c4_team = SequentialAgent(
    name="c4_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        c4_content_analyzer,
        c4_syntax,
        # c4_writer, # TODO temporarily disable the image generation since it's not working well and we want to focus on the content and syntax generation first
    ],
)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction=f"""
    Handoff to 'c4_team' to proceed.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    sub_agents=[c4_team],
)
