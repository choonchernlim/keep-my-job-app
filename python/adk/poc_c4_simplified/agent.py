import logging

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools import exit_loop, ToolContext
from google.genai import types

from .tools import set_c4_field_to_state_tool, set_state_tool, set_new_c4_request_tool, \
    get_next_unprocessed_c4_request_tool, save_processed_c4_request_tool

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
    
    3. For each diagram, call 'set_new_c4_request_tool' to save the diagram type and description.
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
        set_new_c4_request_tool,
    ],
)

c4_processor = Agent(
    name="c4_processor",
    model=model,
    description="Ensure all C4 requests are processed.",
    instruction="""
    ROLE:
    Orchestrator for C4 diagram generation. 
    
    TASKS:
    1. SEARCH: 
        - Call 'get_next_unprocessed_c4_request_tool' to query unprocessed request.
    
    2. IF A REQUEST IS FOUND:
         - Acknowledge the task using this EXACT format: "Processing the next C4 request..."
         - Display the metadata: "Retrieving C4 request (key = [key], type = [diagram_type], description = [description])..."
         - Immediately hand off to the next agent without further chatter.
         - Do NOT call 'exit_loop'.
       
    3. IF NO REQUEST IS FOUND (or status is not successful):
         - State: "No further unprocessed C4 requests found."
         - Call 'exit_loop' immediately.

    STRICT RULES:
    - Never ask the user for permission to proceed; move directly through the flow.
    - Do not summarize the diagram description; output it exactly as retrieved.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        get_next_unprocessed_c4_request_tool,
        exit_loop,
    ],
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
    
    STRICT RULES:
    - DO NOT include introductory text (e.g., "Here is your diagram...").
    - DO NOT include concluding remarks.
    - DO NOT wrap the output in markdown code blocks (no ```mermaid or ```).
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
)

c4_writer = Agent(
    name="c4_writer",
    model=model,
    description="Write mermaid syntax to file.",
    instruction="""
    You are a C4 syntax writer.
    
    1. Call 'save_processed_c4_request_tool' to save the mermaid syntax back to the state.
    2. After the tool returns, immediately state: "C4 syntax has been saved successfully. Task complete."
    3. DO NOT call any tools again after receiving a success message.
    
    mermaid_syntax:
    { mermaid_syntax? }
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[save_processed_c4_request_tool],
)

#
# c4_syntax = Agent(
#     name="c4_syntax",
#     model=model,
#     description="Generate mermaid syntax for C4 diagrams.",
#     instruction="""
#     You are a C4 syntax generator.
#     You will generate mermaid syntax for C4 diagrams based on the diagram type and description stored in the state.
#
#     First, inform the user that you will generate the mermaid syntax for the C4 diagrams based on the diagram type and description stored in the state.
#
#     1. Call 'get_next_c4_from_state_tool' first:
#         - missing_field = mermaid_png_path.
#     2. If object does not exist:
#         - Inform user that all C4 syntax has been generated.
#         - Call 'exit_loop' to exit the loop.
#     3. If object exists:
#         - Inform user that you will generate the mermaid syntax for the object:
#             - Template: "Generating C4 syntax (type = [diagram_type], description = [description])...".
#             - Example: "Generating C4 syntax (type = container, description = ADO pipeline flow)...".
#         - Generate the mermaid syntax based on the diagram_type and description.
#         - Call 'set_c4_field_to_state_tool' to save the mermaid syntax back to the state:
#             - key = [key], field = mermaid_syntax, value = mermaid syntax
#         - Call 'set_state_tool' to set c4_key = [key]. Do not call 'set_state_tool' with other fields.
#     """,
#     generate_content_config=types.GenerateContentConfig(temperature=0),
#     tools=[
#         get_next_c4_from_state_tool,
#         set_c4_field_to_state_tool,
#         set_state_tool,
#         exit_loop,
#     ],
# )

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

c4_diagram_generator_team = LoopAgent(
    name="c4_diagram_generator_team",
    description="Iterates until all C4 diagrams are created.",
    sub_agents=[
        c4_processor,
        c4_syntax,
        c4_writer,
    ],
    max_iterations=2,
)

c4_team = SequentialAgent(
    name="c4_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        c4_content_analyzer,
        c4_diagram_generator_team,
        # c4_syntax_team,
        # c4_writer_team,
    ],
)


# def mock_state(tool_context: ToolContext):
#     tool_context.state.setdefault("c4", {
#         1: {
#             "diagram_type": "context",
#             "description": "this is my context",
#             "processed": False,
#         },
#         2: {
#             "diagram_type": "container",
#             "description": "this is container 1",
#             "processed": False,
#         },
#         3: {
#             "diagram_type": "container",
#             "description": "this is container 2",
#             "processed": False,
#         },
#     })


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
    # tools=[mock_state], # TODO hack
)
