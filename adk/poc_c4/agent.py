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
from typing import List

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


# c4_writer = Agent(
#     name="c4_writer",
#     model=model,
#     description="Generate Mermaid diagram based on the syntax.",
#     instruction="""
#     INSTRUCTIONS:
#     1. The MERMAID_SYNTAX field contains valid Mermaid C4 syntax.
#     2. Call 'generate' tool to create a diagram with the following configuration:
#         - name: test2
#         - folder: ../data/images/
#     2. Call 'save_png_file_as_artifact_tool' to save file as artifact
#     """,
#     tools=[
#         MCPToolset(
#             connection_params=StdioConnectionParams(
#                 server_params=StdioServerParameters(
#                     command="env",
#                     args=[
#                         "CONTENT_IMAGE_SUPPORTED=false",
#                         "npx",
#                         "-y",
#                         "@peng-shawn/mermaid-mcp-server"
#                     ],
#                 ),
#                 timeout=30,
#             ),
#         ),
#         save_png_file_as_artifact_tool,
#     ],
# )

def create_c4_system_context_diagram_agent(state_name: str) -> Agent:
    return Agent(
        name="c4_system_context_diagram",
        model=model,
        description="Create Mermaid system context diagram.",
        instruction="""
        ROLE:
        - You are a Technical Diagram Specialist. 
        - Your specific role is to translate architecture descriptions into valid Mermaid C4 syntax.
        
        INSTRUCTIONS:
        - Analyze the 'REQUEST' to identify all Users, Systems, and Relationships.
        - Generate a system context diagram using ONLY Mermaid 'C4Context' syntax.
        - Apply the **Syntax Guardrails** below to prevent rendering errors.
        - Do not wrap the diagram in any additional text or markdown, return only the Mermaid syntax.
        - When showing the generated Mermaid syntax to the user, wrap it with ```mermaid ... ``` for proper rendering.
        
        SYNTAX GUARDRAILS (CRITICAL):
        - Simple Aliases: All object IDs must be simple alphanumeric strings (e.g., `user1`, `db_core`), with no spaces or hyphens.
        - Only use the following elements: C4Context, Enterprise_Boundary, System_Boundary, Person, Person_Ext, System, System_Ext, SystemDb, SystemDb_Ext, Rel, BiRel, UpdateLayoutConfig.
        - Use %% for comments.
          
        TEMPLATE EXAMPLE:
        C4Context
            title [TITLE] - System Context Diagram
            
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
        output_key=f"{state_name}_MERMAID_SYNTAX",
    )


def create_c4_container_diagram_agent(state_name: str) -> Agent:
    return Agent(
        name="c4_container_diagram",
        model=model,
        description="Create Mermaid container diagram.",
        instruction=f"""
        ROLE:
        - You are a Technical Diagram Specialist. 
        - Your specific role is to translate architecture descriptions into valid Mermaid C4 syntax.
        
        INSTRUCTIONS:
        - Analyze '{state_name}' to identify all Users, Systems, Containers and Relationships.
        - Generate a container diagram using ONLY Mermaid 'C4Container' syntax.
        - Apply the **Syntax Guardrails** below to prevent rendering errors.
        - Do not wrap the diagram in any additional text or markdown, return only the Mermaid syntax.
        - When showing the generated Mermaid syntax to the user, wrap it with ```mermaid ... ``` for proper rendering.
        
        SYNTAX GUARDRAILS (CRITICAL):
        - Simple Aliases: All object IDs must be simple alphanumeric strings (e.g., `user1`, `db_core`), with no spaces or hyphens.
        - Only use the following elements: C4Container, System_Boundary, Person, Person_Ext, System, System_Ext, SystemDb, SystemDb_Ext, Container, Container_Ext, ContainerDb, ContainerDb_Ext, Rel, BiRel, UpdateLayoutConfig.
        - Use %% for comments.
          
        TEMPLATE EXAMPLE:
        C4Container
            title [TITLE] - Container Diagram
        
            Person(user, "Customer")
            System_Ext(mail, "E-Mail System")
            System_Ext(main, "Mainframe")
        
            Container_Boundary(ib, "Internet Banking") {{
                Container(spa, "SPA", "Angular")
                Container(mobile, "Mobile App", "Xamarin")
                Container(web, "Web App", "Spring MVC")
                ContainerDb(db, "Database", "SQL")
                Container(api, "API", "Java")
            }}
        
            %% Relationships
            Rel(user, web, "HTTPS")
            Rel(user, spa, "HTTPS")
            Rel(user, mobile, "Uses")
            Rel(web, spa, "Delivers")
            Rel(spa, api, "JSON/HTTPS")
            Rel(mobile, api, "JSON/HTTPS")
            Rel(mail, user, "E-mails")
            BiRel(api, mail, "SMTP")
            
        C4_CONTAINER:
        {{ {state_name}? }}
        """,
        generate_content_config=types.GenerateContentConfig(temperature=0),
        output_key=f"{state_name}_MERMAID_SYNTAX",
    )


def create_c4_writer_agent(state_name: str) -> Agent:
    return Agent(
        name="c4_writer",
        model=model,
        description="Generate Mermaid diagram based on the syntax.",
        instruction=f"""
        INSTRUCTIONS:
        1. The {state_name}_MERMAID_SYNTAX field contains valid Mermaid C4 syntax.
        2. Call 'generate' tool to create a diagram with the following configuration:
            - name: {state_name}
            - folder: ../data/images/
        3. Call 'save_png_file_as_artifact_tool' to save file as artifact.
        4. Tell the user that the diagram has been created. Do not say anything else.
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


# def create_c4_team_agent(diagram_agent: Agent, writer_agent: Agent) -> SequentialAgent:
#     return SequentialAgent(
#         name="c4_team",
#         description="Create an architecture design and save it as a file.",
#         sub_agents=[
#             diagram_agent,
#             writer_agent,
#         ],
#     )


c4_container_analyzer = Agent(
    name="c4_container_analyzer",
    model=model,
    description="Identify C4 containers in the document.",
    instruction="""
    ROLE:
    You are a C4 Content Analyst. 
    Your specific role is to analyze architecture descriptions and identify C4 containers.
    
    INSTRUCTIONS:
    1. Identify 2 most important C4 containers from the 'REQUEST'.
    2. Provide a brief description for each identified container.
    3. Use 'append_to_state_tool' to save the following info into the state:
        - 'C4_CONTAINER_1' = container 1 description
        - 'C4_CONTAINER_2' = container 2 description
    
    REQUEST:
    { REQUEST? }
    """,
    tools=[
        append_to_state_tool,
    ],
)

c4_team = SequentialAgent(
    name="ux_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        c4_container_analyzer,
        create_c4_system_context_diagram_agent('SYSTEM_CONTEXT'),
        create_c4_writer_agent("SYSTEM_CONTEXT"),
        create_c4_container_diagram_agent('C4_CONTAINER_1'),
        create_c4_writer_agent("C4_CONTAINER_1"),
        create_c4_container_diagram_agent('C4_CONTAINER_2'),
        create_c4_writer_agent("C4_CONTAINER_2"),
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
    sub_agents=[c4_team],
)
