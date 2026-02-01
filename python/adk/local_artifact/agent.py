import logging
import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import ToolContext
from google.genai import types
from google.genai.types import Part

logging.basicConfig(level=logging.INFO)  # or logging.ERROR for only errors

load_dotenv()

model = os.getenv("MODEL")
print(model)


async def save_as_artifact_tool(
        tool_context: ToolContext,
        content: str,
        mime_type: str,
        filename: str,
) -> dict[str, str]:
    image = Part.from_bytes(
        data=content.encode("utf-8"),
        mime_type=mime_type,
    )
    version = await tool_context.save_artifact(filename, image)

    return {"status": "success", "version": version}


root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction=f"""
    1. Create a lorem ipsum paragraph in Markdown format.
    2. Call 'save_as_artifact_tool' to save the content as a Markdown file.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[save_as_artifact_tool],
)
