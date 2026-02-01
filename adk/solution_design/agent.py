import logging
import os
from enum import StrEnum

# from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.tools import exit_loop
# from google.adk.tools.langchain_tool import LangchainTool  # import
from google.genai import types

# cloud_logging_client = google.cloud.logging.Client()
# cloud_logging_client.setup_logging()
from .tools import append_to_state_tool, load_problem_into_state_tool, save_as_artifact_tool

# import google.cloud.logging
# from langchain_community.tools import WikipediaQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper

logging.basicConfig(level=logging.INFO)  # or logging.ERROR for only errors

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)


class Field(StrEnum):
    PROBLEM_NUMBER = "PROBLEM_NUMBER"
    PROBLEM = "PROBLEM"
    PROPOSED_SOLUTION = "PROPOSED_SOLUTION"
    CRITICAL_FEEDBACK = "CRITICAL_FEEDBACK"


technical_writer = Agent(
    name="technical_writer",
    model=model_name,
    description="Saves the approved architecture solution into a document.",
    instruction=f"""
    ROLE: 
    - You are an experienced Technical Writer. 

    INSTRUCTIONS:
    - Review the {Field.PROPOSED_SOLUTION} and create a well-structured document summarizing the architecture design.
    - Use 'save_as_artifact_tool' to create a new Markdown file with the following arguments:
        - For a filename, use this naming convention:
            - [CURRENT DATE]__[{Field.PROBLEM_NUMBER}]__[document title with safe characters].md
            - Example: 2026-01-01__2__patient-data-pipeline.md
        - Write to the 'proposed_solutions' directory.

    PROPOSED_SOLUTION:
    {{ {Field.PROPOSED_SOLUTION}? }}
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[save_as_artifact_tool],
)

architectural_review_board = Agent(
    name="architectural_review_board",
    model=model_name,
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
    # instruction="""
    # INSTRUCTIONS:
    # Consider these questions about the PLOT_OUTLINE:
    # - Does it answer all the questions in the PROBLEM?
    # - Is the proposed solution feasible and practical in a large healthcare organization?
    # - Does it based on the current best practices for cloud architecture?
    # - Does it take account of the non-functional requirements like scalability, availability, privacy and security?
    # - Does it provide sufficient trade-offs where relevant?
    #
    # If the PROPOSED_SOLUTION does a good job with these questions, exit the writing loop with your 'exit_loop'.
    # If significant improvements can be made, use the 'append_to_state_tool' to add your feedback to the field 'CRITICAL_FEEDBACK'.
    # Explain your decision and briefly summarize the feedback you have provided.
    #
    # PROBLEM:
    # { PROBLEM? }
    #
    # PROPOSED_SOLUTION:
    # { PROPOSED_SOLUTION? }
    # """,
    tools=[append_to_state_tool, exit_loop]
)

solution_architect = Agent(
    name="solution_architect",
    model=model_name,
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
        - Embed PHI protection and HIPAA compliance.
        - Explicitly document at least three architectural trade-offs.
    3. Output a structured SAD using Markdown headings and bullet points.
    
    PROBLEM: 
    {{ {Field.PROBLEM}? }}
    
    CRITICAL_FEEDBACK: 
    {{ {Field.CRITICAL_FEEDBACK}? }}
    """,
    # instruction="""
    # ROLE:
    # You are a Principal Solutions Architect. Your role is to perform a structural decomposition
    # of a business problem into a comprehensive technical roadmap.
    #
    # OBJECTIVE:
    # Analyze the provided 'PROBLEM' and propose the production-grade solution.
    #
    # ARCHITECTURAL GUARDRAILS:
    # Your topic selection must ensure the final design addresses:
    #
    # - Core Logic: Functional components required to solve the primary problem.
    # - Non-Functional Requirements: Take account of scalability, high availability, maintainability, and disaster recovery.
    # - Compliance: Alignment with industry standards and best practices).
    # - Cloud Platform: Use Google Cloud Platform services and best practices where applicable.
    #
    # OUTPUT & STATE MANAGEMENT:
    # - Format: Group content by domain. Create a section for each group and use bullet points for clarity.
    # - Use the 'save_to_state_tool' to save the solution to 'PROPOSED_SOLUTION' state.
    #
    # PROBLEM:
    # { PROBLEM? }
    # """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    # tools=[append_to_state_tool],
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
    model=model_name,
    description="Guides the user in creating an architecture design and solution.",
    instruction=f"""
    ROLE:
    You are a helpful engineering solution coordinator.

    # INSTRUCTIONS:
    1. Ask the user for a problem number.
    2. Use 'append_to_state_tool' to save the problem number into the {Field.PROBLEM_NUMBER} field.
    3. Use 'load_problem_into_state_tool' to load the file from the 'problems' directory into the {Field.PROBLEM} field.
    4. Ask the user if they wish to proceed with solution design.
    5. If the user agrees, confirm your support and hand off to the solution_architecture_team.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        append_to_state_tool,
        load_problem_into_state_tool,
    ],
    sub_agents=[solution_architecture_team],
)

#     - Let the user know you will help them write a pitch for a hit movie. Ask them for
#       a historical figure to create a movie about.
#     - When they respond, use the 'append_to_state' tool to store the user's response
#       in the 'PROMPT' state key
