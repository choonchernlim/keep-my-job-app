import os
import logging
# import google.cloud.logging

# from callback_logging import log_query_to_model, log_model_response
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext
# from google.adk.tools.langchain_tool import LangchainTool  # import
from google.genai import types

# from langchain_community.tools import WikipediaQueryRun
# from langchain_community.utilities import WikipediaAPIWrapper

from google.adk.tools import exit_loop

# cloud_logging_client = google.cloud.logging.Client()
# cloud_logging_client.setup_logging()
from .tools import append_to_state_tool, load_problem_into_state_tool, save_to_state_tool

logging.basicConfig(level=logging.INFO)  # or logging.ERROR for only errors

load_dotenv()

model_name = os.getenv("MODEL")
print(model_name)


# Tools


# def write_file(
#         tool_context: ToolContext,
#         directory: str,
#         filename: str,
#         content: str
# ) -> dict[str, str]:
#     target_path = os.path.join(directory, filename)
#     os.makedirs(os.path.dirname(target_path), exist_ok=True)
#     with open(target_path, "w") as f:
#         f.write(content)
#     return {"status": "success"}


# Agents

# box_office_researcher = Agent(
#     name="box_office_researcher",
#     model=model_name,
#     description="Considers the box office potential of this film",
#     instruction="""
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     INSTRUCTIONS:
#     Write a report on the box office potential of a movie like that described in PLOT_OUTLINE based on the reported box office performance of other recent films.
#     """,
#     output_key="box_office_report"
# )
#
# casting_agent = Agent(
#     name="casting_agent",
#     model=model_name,
#     description="Generates casting ideas for this film",
#     instruction="""
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     INSTRUCTIONS:
#     Generate ideas for casting for the characters described in PLOT_OUTLINE
#     by suggesting actors who have received positive feedback from critics and/or
#     fans when they have played similar roles.
#     """,
#     output_key="casting_report"
# )
#
# preproduction_team = ParallelAgent(
#     name="preproduction_team",
#     sub_agents=[
#         box_office_researcher,
#         casting_agent
#     ]
# )
#
# critic = Agent(
#     name="critic",
#     model=model_name,
#     description="Reviews the outline so that it can be improved.",
#     instruction="""
#     INSTRUCTIONS:
#     Consider these questions about the PLOT_OUTLINE:
#     - Does it meet a satisfying three-act cinematic structure?
#     - Do the characters' struggles seem engaging?
#     - Does it feel grounded in a real time period in history?
#     - Does it sufficiently incorporate historical details from the RESEARCH?
#
#     If the PLOT_OUTLINE does a good job with these questions, exit the writing loop with your 'exit_loop' tool.
#     If significant improvements can be made, use the 'append_to_state' tool to add your feedback to the field 'CRITICAL_FEEDBACK'.
#     Explain your decision and briefly summarize the feedback you have provided.
#
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     RESEARCH:
#     { research? }
#     """,
#     before_model_callback=log_query_to_model,
#     after_model_callback=log_model_response,
#     tools=[append_to_state, exit_loop]
# )
#
# file_writer = Agent(
#     name="file_writer",
#     model=model_name,
#     description="Creates marketing details and saves a pitch document.",
#     instruction="""
#     INSTRUCTIONS:
#     - Create a marketable, contemporary movie title suggestion for the movie described in the PLOT_OUTLINE. If a title has been suggested in PLOT_OUTLINE, you can use it, or replace it with a better one.
#     - Use your 'write_file' tool to create a new txt file with the following arguments:
#         - for a filename, use the movie title
#         - Write to the 'movie_pitches' directory.
#         - For the 'content' to write, include:
#             - The PLOT_OUTLINE
#             - The BOX_OFFICE_REPORT
#             - The CASTING_REPORT
#
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     BOX_OFFICE_REPORT:
#     { box_office_report? }
#
#     CASTING_REPORT:
#     { casting_report? }
#     """,
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0,
#     ),
#     tools=[write_file],
# )
#
# screenwriter = Agent(
#     name="screenwriter",
#     model=model_name,
#     description="As a screenwriter, write a logline and plot outline for a biopic about a historical character.",
#     instruction="""
#     INSTRUCTIONS:
#     Your goal is to write a logline and three-act plot outline for an inspiring movie about the historical character(s) described by the PROMPT: { PROMPT? }
#
#     - If there is CRITICAL_FEEDBACK, use those thoughts to improve upon the outline.
#     - If there is RESEARCH provided, feel free to use details from it, but you are not required to use it all.
#     - If there is a PLOT_OUTLINE, improve upon it.
#     - Use the 'append_to_state' tool to write your logline and three-act plot outline to the field 'PLOT_OUTLINE'.
#     - Summarize what you focused on in this pass.
#
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     RESEARCH:
#     { research? }
#
#     CRITICAL_FEEDBACK:
#     { CRITICAL_FEEDBACK? }
#     """,
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0,
#     ),
#     tools=[append_to_state],
# )
#
# researcher = Agent(
#     name="researcher",
#     model=model_name,
#     description="Answer research questions using Wikipedia.",
#     instruction="""
#     PROMPT:
#     { PROMPT? }
#
#     PLOT_OUTLINE:
#     { PLOT_OUTLINE? }
#
#     CRITICAL_FEEDBACK:
#     { CRITICAL_FEEDBACK? }
#
#     INSTRUCTIONS:
#     - If there is a CRITICAL_FEEDBACK, use your wikipedia tool to do research to solve those suggestions
#     - If there is a PLOT_OUTLINE, use your wikipedia tool to do research to add more historical detail
#     - If these are empty, use your Wikipedia tool to gather facts about the person in the PROMPT
#     - Use the 'append_to_state' tool to add your research to the field 'research'.
#     - Summarize what you have learned.
#     Now, use your Wikipedia tool to do research.
#     """,
#     generate_content_config=types.GenerateContentConfig(
#         temperature=0,
#     ),
#     tools=[
#         LangchainTool(tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())),
#         append_to_state,
#     ],
# )
#
# writers_room = LoopAgent(
#     name="writers_room",
#     description="Iterates through research and writing to improve a movie plot outline.",
#     sub_agents=[
#         researcher,
#         screenwriter,
#         critic
#     ],
#     max_iterations=5,
# )
#
# film_concept_team = SequentialAgent(
#     name="film_concept_team",
#     description="Write a film plot outline and save it as a text file.",
#     sub_agents=[
#         writers_room,
#         preproduction_team,
#         file_writer
#     ],
# )

# class DynamicTopicResearcher(Agent):
#     def __init__(self, model):
#         # We don't need instructions here because this agent's sole job
#         # is to manage the sub-agents.
#         super().__init__(name="dynamic_research_manager")
#         self.model = model
#
#     def run(self, state: dict) -> dict:
#         # 1. READ the topics from the state (populated by the previous agent)
#         topics = state.get("TOPIC_LIST", [])
#
#         if not topics:
#             return {"error": "No topics found in TOPIC_LIST"}
#
#         print(f"--- Manager: Spawning {len(topics)} researchers ---")
#
#         # 2. CREATE the sub-agents dynamically
#         research_agents = []
#         for i, topic in enumerate(topics):
#             # Create a dedicated agent for this specific topic
#             agent = Agent(
#                 name=f"researcher_{i}",
#                 model=self.model,
#                 # Inject the topic directly into the instruction
#                 instruction=f"""
#                     You are an expert technical researcher.
#
#                     TOPIC: "{topic}"
#                     PROBLEM_SET: {{ PROBLEM_SET? }}
#
#                     Provide a detailed technical breakdown of this topic.
#                     Focus on: Architecture, Scalability, and Security.
#                 """,
#                 # Ensure they write to unique keys so they don't overwrite each other
#                 output_key=f"RESEARCH_RESULT_{i}"
#             )
#             research_agents.append(agent)
#
#         # 3. EXECUTE them in parallel
#         # We instantiate a ParallelAgent on the fly and run it immediately
#         parallel_team = ParallelAgent(
#             name="temp_parallel_team",
#             sub_agents=research_agents
#         )
#
#         # This returns the combined state from all researchers
#         return parallel_team.run(state=state)
#
#
# research_manager = DynamicTopicResearcher(model=model_name)
#
# topic_generator = Agent(
#     name="topic_generator",
#     model=model_name,
#     description="Generate key topics to address the problem set.",
#     instruction="""
#     PROBLEM_STATEMENT:
#     { PROBLEM_STATEMENT? }
#
#     ROLE:
#     You are a Senior Principal Solutions Architect. Your role is to perform a structural decomposition
#     of a business problem into a comprehensive technical roadmap.
#
#     OBJECTIVE:
#     Analyze the provided PROBLEM_STATEMENT and extract 5 most important of Key Architectural Topics.
#     These topics will serve as the foundational headers for downstream agents to generate
#     detailed technical specifications.
#
#     ARCHITECTURAL GUARDRAILS:
#     Your topic selection must ensure the final design addresses:
#
#     - Core Logic: Functional components required to solve the primary problem.
#     - Non-Functional Requirements: Scalability, high availability, maintainability, and disaster recovery.
#     - Security by Design: Identity & Access Management (IAM), data encryption (at rest/in transit), and the principle of least privilege.
#     - Efficiency: Cost-optimization, resource utilization, and performance bottlenecks.
#     - Compliance: Alignment with industry standards (e.g., SOC2, GDPR, or domain-specific best practices).
#     - Cloud Platform: Use Google Cloud Platform services and best practices where applicable.
#
#     TASK REQUIREMENTS:
#     - Deconstruction: Break the PROBLEM_STATEMENT into logical domains (e.g., Data Tier, API Layer, Security, Infrastructure).
#     - Specificity: Avoid generic topics. Instead of "Security," use "Authentication and Zero-Trust Authorization Framework."
#     - Logical Flow: Organize topics in the order they should be addressed (e.g., Infrastructure/Data before Frontend/UI).
#     - Conciseness: Provide only the topic titles or short descriptive phrases. Do not generate the technical content itself.
#
#     OUTPUT & STATE MANAGEMENT:
#     - Validation: Review the generated list to ensure each topic is distinct and specific.
#     - Format: Prepare the topics as a JSON array of strings (e.g., ["Topic 1", "Topic 2", "Topic 3"]).
#     - Tool Call: Use the append_to_state tool with the following parameters:
#         - state_key: 'TOPIC_LIST'
#         - value: The array of strings generated above.
#     - Important: Do NOT pass the list as a single newline-separated string. Ensure the tool is called with the array
#       format so that each topic is stored as an individual element in the state.
#     """,
#     generate_content_config=types.GenerateContentConfig(temperature=0),
#     tools=[append_to_state_tool],
# )
#

solution_architect = Agent(
    name="solution_architect",
    model=model_name,
    description="Propose an engineering solution based on the question.",
    instruction="""
    ROLE:
    - You are a Principal Solutions Architect. Your goal is to transform a complex problem statement into a professional, industry-standard Solution Architecture Document. 
    - You design systems that are resilient, scalable, and tailored for highly regulated environments like healthcare.

    INSTRUCTIONS
    - Generate a comprehensive architecture design based on the provided `PROBLEM`. 
    - Ensure all 'CRITICAL_FEEDBACK' from previous reviews is addressed in your design.
    - Your response must follow the Industry-Standard Architecture Template below.

    ARCHITECTURAL GUARDRAILS:
    Your topic selection must ensure the final design addresses:

    - Core Logic: Functional components required to solve the primary problem.
    - Non-Functional Requirements: Take account of scalability, high availability, maintainability, and disaster recovery.
    - Security by Design: Especially regarding PHI and HIPAA compliance.
    - Compliance: Alignment with industry standards and best practices).
    - Cloud Platform: Use Google Cloud Platform services and best practices where applicable.
    - Cloud-Native Maturity: Prefer managed services to reduce operational overhead.
    - Resiliency: Assume everything fails; design for high availability.

    OUTPUT & STATE MANAGEMENT:
    - Output the design using clear Markdown headings, bullet points, and table formats for the technology stack.

    SOLUTION ARCHITECTURE DOCUMENT TEMPLATE:
    1. Executive Summary
        - Provide a high-level overview of the proposed solution (2-3 sentences).
        - State the primary value proposition (e.g., "Reduces latency by 40% while ensuring 99.9% uptime").
    
    2. Proposed Architecture Design
        - Conceptual Overview: Describe the "Big Picture" logic of how the system works.
        - Component Breakdown: List the key services (e.g., API Gateway, Message Queues, Databases) and their specific roles.
        - Data Flow: Describe how data moves through the system from ingestion to storage/output.
    
    3. Technology Stack
        - List the specific tools and cloud services (e.g., Python/FastAPI, PostgreSQL, Redis, Kubernetes).
        - Briefly justify why these were chosen over alternatives.
    
    4. Addressing Non-Functional Requirements (The "ilities")
        - Scalability: How does the system handle growth (Vertical vs. Horizontal)?
        - Availability/DR: What is the Multi-AZ or Multi-Region strategy?
        - Security & Compliance: Detail encryption (at rest/in transit), Identity & Access Management (IAM), and audit logging.
    
    5. Trade-offs and Constraints
        - Identify at least two significant trade-offs (e.g., "Choosing Consistency over Availability (CAP Theorem) because of financial data accuracy requirements").
        - List any known limitations of this design.
    
    6. Implementation Roadmap (Phased Approach)
        - Phase 1 (MVP): Core functionality.
        - Phase 2 (Scale): Optimization and advanced features.
    
    PROBLEM:
    { PROBLEM? }

    CRITICAL_FEEDBACK:
    { CRITICAL_FEEDBACK? }
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
    output_key="PROPOSED_SOLUTION",
)

critic = Agent(
    name="critic",
    model=model_name,
    description="Reviews the outline so that it can be improved.",
    instruction="""
    ROLE: 
    You are the Lead of the Architectural Review Board (ARB). Your role is to provide a rigorous, 
    objective "Cold Eye" review of proposed designs to ensure they are production-ready for a 
    global healthcare enterprise.

    INSTRUCTIONS: 
    Critique the PROPOSED_SOLUTION through the lens of Architectural Governance. 
    You are not here to "rubber-stamp" the design; you are here to identify risks. 
    
    Evaluate the following:
    - Requirement Integrity: Does the design solve the actual PROBLEM, or has it drifted into over-engineering?
    - Healthcare Guardrails: Does the architecture inherently protect PHI? Look for gaps in encryption, audit logging, and data residency.
    - Operational Viability: Is this solution "day-two" ready? Assess if it’s too complex for a standard SRE team to manage.
    - Modern Standards: Does it align with current Well-Architected Frameworks (e.g., GCP/AWS/Azure best practices)?
    - Omission Check: What is missing? Check for lack of disaster recovery, monitoring, or cost-management strategies.

    DECISION LOGIC:
    - If the PROPOSED_SOLUTION is robust and risk-mitigated, call 'exit_loop'.
    - If significant improvements can be made, use the 'append_to_state_tool' to add your feedback to the field 'CRITICAL_FEEDBACK'.
    - Explain your decision and briefly summarize the feedback you have provided.
                
    PROBLEM:
    { PROBLEM? }
    
    PROPOSED_SOLUTION:
    { PROPOSED_SOLUTION? }
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

solutioning_room = LoopAgent(
    name="solutioning_room",
    description="Iterates through research and writing to improve the proposed solution.",
    sub_agents=[
        solution_architect,
        critic,
    ],
    max_iterations=3,
)

solution_architecture_team = SequentialAgent(
    name="solution_architecture_team",
    description="Create an architecture design and save it as a text file.",
    sub_agents=[
        solutioning_room,
    ],
)

root_agent = Agent(
    name="root_agent",
    model=model_name,
    description="Guides the user in creating an architecture design and solution.",
    instruction="""
        - Ask user what question number to load.
        - When the user provides the question number, use the 'load_problem_into_state_tool' tool to 
            load the problem from 'problems' directory into field 'PROBLEM'.
        - When a problem is loaded, summarize it for the user and ask if the user would like to proceed with solution design.
        - If the user agrees, let them know you will help them work through it.
        - Hand off to the 'solution_architecture_team' to do the solution design.
    """,
    #         - When a question is loaded, acknowledge it and let the user know you will help them work through it.
    #         - Hand off to the 'solution_architecture_team' to do the solution design.
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[load_problem_into_state_tool],
    sub_agents=[solution_architecture_team],
)

#     - Let the user know you will help them write a pitch for a hit movie. Ask them for
#       a historical figure to create a movie about.
#     - When they respond, use the 'append_to_state' tool to store the user's response
#       in the 'PROMPT' state key
