import logging
import os
from enum import StrEnum

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools import exit_loop
from google.genai import types

from .tools import append_to_state_tool, load_data_into_state_tool, save_as_artifact_tool

logging.basicConfig(level=logging.INFO)

load_dotenv()

model = os.getenv("MODEL")

class Field(StrEnum):
    PROBLEM_FILENAME = "PROBLEM_FILENAME"
    PROBLEM = "PROBLEM"
    PROPOSED_SOLUTION = "PROPOSED_SOLUTION"
    CRITICAL_FEEDBACK = "CRITICAL_FEEDBACK"


technical_writer = Agent(
    name="technical_writer",
    model=model,
    description="Saves the approved architecture solution into a document.",
    instruction=f"""
    ROLE: 
    - You are an experienced Technical Writer. 

    INSTRUCTIONS:
    - Review the {Field.PROPOSED_SOLUTION} and create a well-structured Solution Architecture Document summarizing the architecture design.
    - Use 'save_as_artifact_tool' to create a new Markdown file with the following arguments:
        - For a filename, use this naming convention:
            - [CURRENT DATE]__[{Field.PROBLEM_FILENAME} with safe characters]__[document title with safe characters].md
            - Example: 2026-01-01__filename-txt__patient-data-pipeline.md
        - Write to the 'proposed_solutions' directory.

    PROPOSED_SOLUTION:
    {{ {Field.PROPOSED_SOLUTION}? }}
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[save_as_artifact_tool],
)

architectural_review_board = Agent(
    name="architectural_review_board",
    model=model,
    description="Reviews the outline so that it can be improved.",
    instruction=f"""
    ROLE: 
    - You are the Lead of the Architectural Review Board. 
    - Your role is to provide a rigorous, objective "Cold Eye" review of proposed designs to ensure they are 
      production-ready for a healthcare enterprise.

    INSTRUCTIONS: 
    - Critique the {Field.PROPOSED_SOLUTION} through the lens of Architectural Governance. 
    - You are not here to "rubber-stamp" the design; you are here to identify risks. 
    
    Evaluate the following:
    - Does the design solve the actual {Field.PROBLEM}, or has it drifted into over-engineering?
    - Does the design answers all the questions described in {Field.PROBLEM}?
    - Does the architecture inherently protect PHI? Look for gaps in encryption, audit logging, and data residency.
    - Is this solution "day-two" ready? Assess if it’s too complex for a standard SRE team to manage.
    - Does it align with current Well-Architected Frameworks (e.g., GCP best practices)?
    - What is missing? Check for lack of disaster recovery, monitoring, or cost-management strategies.

    DECISION LOGIC:
    - If the {Field.PROPOSED_SOLUTION} is robust and risk-mitigated, call 'exit_loop'.
    - If significant improvements can be made, use the 'append_to_state_tool' to add your feedback to the field {Field.CRITICAL_FEEDBACK}.
    - Explain your decision and briefly summarize the feedback you have provided.
                
    PROBLEM:
    {{ {Field.PROBLEM}? }}
    
    PROPOSED_SOLUTION:
    {{ {Field.PROPOSED_SOLUTION}? }}
    """,
    tools=[append_to_state_tool, exit_loop]
)

solution_architect = Agent(
    name="solution_architect",
    model=model,
    description="Propose an engineering solution based on the problem.",
    instruction=f"""
    ROLE:
    You are a knowledgeable Principal Solutions Architect, specializing in designing
    cloud-native architectures for healthcare enterprises.

    INSTRUCTIONS:
    1. Evaluate the {Field.PROBLEM} alongside any {Field.CRITICAL_FEEDBACK} to ensure iterative improvement.
    2. Architect a solution strictly adhering to these Guardrails:
        - Use GCP managed services and cloud-native patterns for core functional components.
        - Ensure high availability, scalability, security and disaster recovery.
        - Take account of maintainability, operational simplicity, and cost-efficiency.
        - Adhere to healthcare industry compliance standards (privacy, legal, security) and best practices.
        - Explicitly document at least three architectural trade-offs.
    3. Output a structured Solution Architecture Document using Markdown headings and bullet points.
    
    PROBLEM: 
    {{ {Field.PROBLEM}? }}
    
    CRITICAL_FEEDBACK: 
    {{ {Field.CRITICAL_FEEDBACK}? }}
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    output_key=Field.PROPOSED_SOLUTION,
)

solutioning_room = LoopAgent(
    name="solutioning_room",
    description="Iterates through research and writing to improve the proposed solution.",
    sub_agents=[
        solution_architect,
        architectural_review_board,
    ],
    max_iterations=3,
)

solution_architecture_team = SequentialAgent(
    name="solution_architecture_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        solutioning_room,
        technical_writer,
    ],
)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Guides the user in creating an architecture design and solution.",
    instruction=f"""
    ROLE:
    You are a helpful engineering solution coordinator.

    # INSTRUCTIONS:
    1. Ask the user for filename (ex: filename.txt) to load from 'problems' directory.
    2. Use 'append_to_state_tool' to save the filename into the {Field.PROBLEM_FILENAME} field.
    3. Use 'load_data_into_state_tool' to load the file from the 'problems' directory into the {Field.PROBLEM} field.
    4. Ask the user if they wish to proceed with solution design.
    5. If the user agrees, confirm your support and hand off to the solution_architecture_team.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        append_to_state_tool,
        load_data_into_state_tool,
    ],
    sub_agents=[solution_architecture_team],
)
