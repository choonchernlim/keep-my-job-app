import logging
import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.models import LiteLlm
from google.adk.tools import ToolContext
from google.genai import types

load_dotenv()

model = LiteLlm(model=os.getenv("MODEL")) if os.getenv("LITELLM") else os.getenv("MODEL")
logging.info(model)


def append_to_state_tool(
        tool_context: ToolContext,
        field: str,
        response: str) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
        :param tool_context: tool context
        :param field: a field name to append to
        :param response: a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    # list all fields in the state for debugging

    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")

    logging.info(f"[########] {tool_context.state.to_dict()}")

    return {"status": "success"}


def set_c4_to_state_tool(
        tool_context: ToolContext,
        key: int,
        diagram_type: str,  # context or container
        description: str,
        mermaid_syntax: str = None) -> dict[str, str]:
    tool_context.state["c4"] = tool_context.state.get("c4", {})
    tool_context.state["c4"][key] = {
        "diagram_type": diagram_type,
        "description": description,
        "mermaid_syntax": mermaid_syntax,
    }

    return {"status": "success"}


def set_c4_field_to_state_tool(
        tool_context: ToolContext,
        key: int,
        field: str,
        value: str) -> dict[str, str]:
    tool_context.state["c4"] = tool_context.state.get("c4", {})

    if key not in tool_context.state["c4"]:
        tool_context.state["c4"][key] = {}

    tool_context.state["c4"][key][field] = value

    return {"status": "success"}


def get_next_c4_from_state_tool(
        tool_context: ToolContext,
        missing_field: str) -> dict[str, str] | None:
    tool_context.state["c4"] = tool_context.state.get("c4", {})

    for key, info in tool_context.state["c4"].items():
        if missing_field not in info:
            return {
                "key": key,
                "diagram_type": info["diagram_type"],
                "description": info["description"],
            }

    return None


c4_content_analyzer = Agent(
    name="c4_content_analyzer",
    model=model,
    description="Set C4 states.",
    instruction="""
    Use 'set_c4_field_to_state_tool' to save the following info into the state:
        - key = 1, diagram_type = context, description = "this is my context"
        - key = 2, diagram_type = container, description = "this is container 1"
        - key = 3, diagram_type = container, description = "this is container 2"
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
    1. Use 'get_next_c4_from_state_tool' to get the next object without mermaid_syntax.
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
    1. Use 'get_next_c4_from_state_tool' to get the next object without mermaid_png_path.
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
        c4_writer,
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
