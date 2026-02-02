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

# logging.basicConfig(level=logging.INFO)  # or logging.ERROR for only errors

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)


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


async def save_image_as_artifact_tool(
        tool_context: ToolContext,
        image: bytes,
        filename: str,
) -> dict[str, str]:
    image = Part.from_bytes(
        data=image,
        mime_type="image/png",
    )
    version = await tool_context.save_artifact(filename, image)

    return {"status": "success", "version": version}


diagram_writer = Agent(
    name="diagram_writer",
    model=model_name,
    description="Write Mermaid diagram.",
    instruction="""
    INSTRUCTIONS:
    1. Call 'generate_mermaid_diagram' tool to produce a diagram.
    2. Save the PNG as an artifact using 'save_image_as_artifact_tool'.
    3. Present the artifact to the user to view.

    MERMAID_SYNTAX:
    { MERMAID_SYNTAX? }
    """,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='python',
                    args=["proxy_mermaid.py"],
                ),
            ),
        ),
        save_image_as_artifact_tool,
    ]
)

diagram_specialist = Agent(
    name="diagram_specialist",
    model=model_name,
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
    model=model_name,
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
