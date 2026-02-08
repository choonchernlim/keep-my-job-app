import logging

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools import exit_loop
from google.genai import types

from .tools import set_c4_field_to_state_tool, get_next_c4_from_state_tool, set_state_tool

load_dotenv()

from shared.model import get_model

model = get_model()
logging.info(model)

c4_content_analyzer = Agent(
    name="c4_content_analyzer",
    model=model,
    description="Set C4 states.",
    instruction="""
    1. Inform user that you will analyze the content to determine the right C4 diagrams to create.
    
    2. Create 3 diagrams:
        - context = this is my context
        - container = this is my container 1
        - container = this is my container 2
    
    3. For each diagram, perform the following steps:
        - Increment the key
        - Call 'set_c4_field_to_state_tool' to save the diagram type into the state.
        - Call 'set_c4_field_to_state_tool' to save the description into the state.
    """,
    # instruction="""
    # Call 'set_c4_field_to_state_tool' 6 times to save the following info into the state:
    # - key = 1, field = diagram_type, value = context
    # - key = 1, field = description, value = this is my context
    # - key = 2, field = diagram_type, value = container
    # - key = 2, field = description, value = this is container 1
    # - key = 3, field = diagram_type, value = container
    # - key = 3, field = description, value = this is container 2
    # """,
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
    You are a C4 syntax generator. 
    You will generate mermaid syntax for C4 diagrams based on the diagram type and description stored in the state. 
    
    1. Call 'get_next_c4_from_state_tool':
        - missing_field = mermaid_png_path.
    2. If object exists:
        - Inform user that you will generate the mermaid syntax for the object:
            - Template: "Generating C4 syntax (type = [diagram_type], description = [description])...".
            - Example: "Generating C4 syntax (type = container, description = ADO pipeline flow)...".
        - Generate the mermaid syntax based on the diagram_type and description.
        - Call 'set_c4_field_to_state_tool' to save the mermaid syntax back to the state:
            - key = [key], field = mermaid_syntax, value = mermaid syntax
        - Call 'set_state_tool' to set c4_key = [key]
    3. If object does not exist:
        - Inform user that all C4 syntax has been generated.
        - Call 'exit_loop' to exit the loop.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        get_next_c4_from_state_tool,
        set_c4_field_to_state_tool,
        set_state_tool,
        exit_loop,
    ],
)

# c4_writer = Agent(
#     name="c4_writer",
#     model=model,
#     description="Generate mermaid image.",
#     instruction="""
#     1. Call 'get_next_c4_from_state_tool' to find object with missing mermaid_png_path field.
#     2. If object exists:
#         - Inform that you will generate the mermaid image for the object, example:
#             - Template: "Generating C4 image (type = [diagram_type], description = [description])...".
#             - Example: "Generating C4 image (type = container, description = ADO pipeline flow)...".
#         - Generate the mermaid PNG file based on the mermaid_syntax.
#         - Use 'set_c4_field_to_state_tool' to save the mermaid syntax back to the state:
#             - mermaid_png_path = "/path/to/png"
#         - Call the same agent again.
#     3. If object does not exist:
#         - Inform user that all C4 diagrams have been generated.
#     """,
#     generate_content_config=types.GenerateContentConfig(temperature=0),
#     tools=[
#         get_next_c4_from_state_tool,
#         set_c4_field_to_state_tool,
#     ],
# )

c4_syntax_team = LoopAgent(
    name="c4_syntax_team",
    description="Iterates until all C4 diagrams are created.",
    sub_agents=[
        c4_syntax,
    ],
    max_iterations=5,
)

c4_team = SequentialAgent(
    name="c4_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        c4_content_analyzer,
        # c4_syntax_team,
        # c4_writer_team,
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
