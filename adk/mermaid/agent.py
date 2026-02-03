import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, \
    StdioServerParameters, StdioConnectionParams
from google.genai.types import Part

load_dotenv()

model = os.getenv("MODEL")
print(model)


async def save_image_as_artifact_tool(
        tool_context: ToolContext,
        png_path: str,
        mime_type: str,
) -> dict[str, str]:
    # 1. FIX: Derive the filename from the path (or pass it as an argument)
    filename = os.path.basename(png_path)

    # 2. FIX: Read the actual bytes from the file
    # Part.from_bytes expects 'bytes', not a string path
    with open(png_path, "rb") as f:
        image_data = f.read()

    image = Part.from_bytes(
        data=image_data,
        mime_type=mime_type,
    )

    # 3. Save using the defined filename and the byte content
    version = await tool_context.save_artifact(filename, image)

    return {"status": "success", "version": version}


# save_to_artifact = Agent(
#     name="save_to_artifact",
#     model=model,
#     description="Save Mermaid diagram.",
#     instruction="""
#     INSTRUCTIONS:
#     1. Use 'save_image_as_artifact_tool' to save 'mermaid_image'
#     """,
#     tools=[
#         save_image_as_artifact_tool,
#     ],
# )

mermaid = Agent(
    name="mermaid",
    model=model,
    description="Generate Mermaid diagram.",
    instruction="""
    INSTRUCTIONS:
    1. Call 'generate' tool to create a diagram with the following configuration:
        - name: test2
        - folder: ../data/images/
    2. Call 'save_image_as_artifact_tool' to save file as artifact
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="env",
                    args=[
                        "CONTENT_IMAGE_SUPPORTED=false",
                        "npx",
                        "-y",
                        "@peng-shawn/mermaid-mcp-server"
                    ],
                ),
                timeout=30,
            ),
        ),
        save_image_as_artifact_tool,
    ],
)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Generate Mermaid diagram.",
    instruction="""
    INSTRUCTIONS:
    1. Pass user's mermaid syntax to 'diagram_team'.
    

    MERMAID_SYNTAX:
flowchart TD
A[Christmas] -->|Get money| B(Go shopping)
B --> C{Let me think}
C -->|One| D[Laptop]
C -->|Two| E[iPhone]
C -->|Three| F[fa:fa-car Car]
    """,
    sub_agents=[mermaid],
)
