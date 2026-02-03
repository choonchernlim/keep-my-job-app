import logging
import os

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools import ToolContext
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, \
    StdioServerParameters, StdioConnectionParams
from google.genai import types
from google.genai.types import Part

load_dotenv()

model = os.getenv("MODEL")
print(model)


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
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")

    return {"status": "success"}


# async def save_image_as_artifact_tool(
#         tool_context: ToolContext,
#         image: bytes,
#         filename: str,
# ) -> dict[str, str]:
#     image = Part.from_bytes(
#         data=image,
#         mime_type="image/png",
#     )
#     version = await tool_context.save_artifact(filename, image)
#
#     return {"status": "success", "version": version}


async def save_png_file_as_artifact_tool(
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


diagram_writer = Agent(
    name="diagram_writer",
    model=model,
    description="Generate Mermaid diagram.",
    instruction="""
    INSTRUCTIONS:
    1. Call 'generate' tool to create a diagram with the following configuration:
        - name: test2
        - folder: ../data/images/
    2. Call 'save_png_file_as_artifact_tool' to save file as artifact
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
        save_png_file_as_artifact_tool,
    ],
)

diagram_specialist = Agent(
    name="diagram_specialist",
    model=model,
    description="Create Mermaid diagram.",
    instruction="""
    ROLE:
    - You are a Technical Diagram Specialist. 
    - Your specific role is to translate architecture descriptions into valid Mermaid C4Context syntax.
    
    INSTRUCTIONS:
    1. Analyze the 'REQUEST' to identify all Users, Systems, and Relationships.
    2. Generate the diagram using ONLY Mermaid 'C4Context' syntax.
    3. Apply the **Syntax Guardrails** below to prevent rendering errors.
    4. Do not wrap the diagram in any additional text or markdown, return only the Mermaid syntax.
    
    SYNTAX GUARDRAILS (CRITICAL):
    - No Parentheses in Text: You strictly FORBIDDEN from using `(` or `)` inside any label or description string. 
    -   Bad: `System(sys1, "Gateway (Legacy)")`
    -   Good: `System(sys1, "Gateway - Legacy")`
    - Simple Aliases: All object IDs must be simple alphanumeric strings (e.g., `user1`, `db_core`), with no spaces or hyphens.
    - container vs system: Since C4Context does not support `Container`, map any specific microservices or databases to `System` or `SystemDb`.
    - Only use the following elements: C4Context Enterprise_Boundary, System_Boundary, Person, Person_Ext, System, System_Ext, SystemDb, SystemDb_Ext, Rel, and BiRel.
    - Use %% for comments.
      
    TEMPLATE EXAMPLE:
    C4Context
        Enterprise_Boundary(b0, "My Organization") {
            Person(user1, "User Name", "Description of user")
            
            System_Boundary(b1, "Cluster Name") {
                System(sys1, "System Name", "Description")
                SystemDb(db1, "Database Name", "Description")
            }
        }
        
        %% Relationships
        Rel(user1, sys1, "Uses", "HTTPS")
        BiRel(sys1, db1, "Reads/Writes")
    
    REQUEST:
    { REQUEST? }
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    output_key="MERMAID_SYNTAX"
)

ux_team = SequentialAgent(
    name="ux_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        diagram_specialist,
        diagram_writer,
    ],
)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction=f"""
    You are a Principal Solutions Architect.
    
    INSTRUCTIONS:
    1. Ask user to provide architecture solution to be converted into a diagram.
    2. Use 'append_to_state_tool' to store user's diagram request in REQUEST field.
    3. Handoff to 'ux_team' to create the diagram.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[append_to_state_tool],
    sub_agents=[ux_team],
)
