from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import exit_loop
from google.adk.tools.mcp_tool import MCPToolset, StdioConnectionParams
from google.genai import types
from google.genai.types import Content
from mcp import StdioServerParameters

from .callbacks import display_tool_state, display_agent_state
from .tools import save_new_c4_request_tool, \
    get_next_unprocessed_c4_request_tool, save_processed_c4_request_tool, save_png_file_as_artifact_tool

load_dotenv()

from shared.model import get_model

model = get_model()

c4_content_analyzer = Agent(
    name="c4_content_analyzer",
    model=model,
    description="Set C4 states.",
    instruction="""
    1. Inform user that you will analyze the content to determine the right C4 diagrams to create.
    
    2. Based on architecture_solution, identify 1 context diagram and 2 container diagrams:
        - Template:
            - [type]:
                - "context" or "container"
            - [description]:
                - A summary of what the diagram should contain, based on the architecture solution.
                - Focus on key components and user interactions.
        - Example:
            - context = this is my context
            - container = this is my container 1
            - container = this is my container 2
    
    3. For each diagram, call 'save_new_c4_request_tool' to save the diagram type and description.
    
    4. Inform user that the analysis is complete and you have saved 3 C4 diagram requests to the state.
    
    ARCHITECTURE SOLUTION:
    { architecture_solution }
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        save_new_c4_request_tool,
    ],
    before_tool_callback=display_tool_state,
    before_agent_callback=display_agent_state,
)

c4_processor = Agent(
    name="c4_processor",
    model=model,
    description="Ensure all C4 requests are processed.",
    instruction="""
    ROLE: Orchestrator for C4 diagram generation.
    
    TASKS:
    1. Call 'get_next_unprocessed_c4_request_tool'.
    2. Review the TOOL OUTPUT:
       - IF output contains 'status': 'success':
           a. Announce: "Processing C4 request (key = [key], type = [diagram_type], description = [description])..." using the values returned by the tool.
           b. Hand off to the next agent immediately.
       
       - IF output contains 'status': 'not_found':
           a. Announce: "No further unprocessed requests."
           b. Call 'exit_loop'    
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        get_next_unprocessed_c4_request_tool,
        exit_loop,
    ],
    before_tool_callback=display_tool_state,
    before_agent_callback=display_agent_state,
)

c4_syntax = Agent(
    name="c4_syntax",
    model=model,
    description="Generate mermaid syntax for C4 diagrams.",
    instruction="""
    ROLE: 
    - Strict C4 Mermaid Syntax Generator.
    
    TASKS:
    - Generate ONLY the raw Mermaid code for a C4 diagram.
    - Display the output in markdown code blocks (```mermaid ```).
    
    STRICT RULES:
    - DO NOT include introductory text (e.g., "Here is your diagram...").
    - DO NOT include concluding remarks.
    - Output MUST start directly with the diagram declaration (e.g., C4Context, C4Container).
    - If you cannot generate the syntax, return an empty string.
   
    INPUT DATA:
    
    diagram_type:
    { diagram_type? }

    description:
    { description? }
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    output_key="mermaid_syntax",
    before_tool_callback=display_tool_state,
    before_agent_callback=display_agent_state,
)

c4_writer = Agent(
    name="c4_writer",
    model=model,
    description="Write mermaid syntax to file.",
    instruction="""
    You are a C4 syntax writer.
    
    1. Call 'generate' tool to create a diagram with the following configuration:
        - code: Use mermaid syntax below.
        - name: { png_filename }. Do not suffix with .png, the tool will handle it.
        - folder: { png_directory_path }
    2. Call 'save_png_file_as_artifact_tool' to save the generated PNG file:
        - png_filename: { png_filename }
        - png_directory_path: { png_directory_path }
    3. Call 'save_processed_c4_request_tool' to save the mermaid syntax back to the state.
    4. After the tool returns, immediately state: "C4 syntax has been saved successfully. Task complete."
    5. DO NOT call any tools again after receiving a success message.
    
    MERMAID SYNTAX:
    { mermaid_syntax }
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
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
        save_processed_c4_request_tool,
    ],
    before_tool_callback=display_tool_state,
    before_agent_callback=display_agent_state,
)

c4_diagram_generator_team = LoopAgent(
    name="c4_diagram_generator_team",
    description="Iterates until all C4 diagrams are created.",
    sub_agents=[
        c4_processor,
        c4_syntax,
        c4_writer,
    ],
    max_iterations=5,
)

c4_team = SequentialAgent(
    name="c4_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        c4_content_analyzer,
        # c4_diagram_generator_team, # TODO temp disabled
    ],
)

def inject_state(callback_context: CallbackContext) -> Optional[Content]:
    callback_context.state.update({
        "architecture_solution":  Path("../../data/proposed_solutions/2024-07-30__1__shared-enterprise-platform-architecture.md").read_text(),
    })

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction=f"""
    1. Handoff to 'c4_team' to proceed.
    """,
    # instruction=f"""
    # 1. Call 'mock_state' tool first.
    # 2. Handoff to 'c4_team' to proceed.
    # """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    sub_agents=[c4_team],
    before_agent_callback=inject_state, # TODO temp hack to inject state without a tool. Replace with a proper tool in the future.

)
