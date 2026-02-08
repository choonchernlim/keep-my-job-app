import logging

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models import LiteLlm
from google.genai import types

load_dotenv()

# model = LiteLlm(
#     model="openai/qwen3:8b",
#     extra_body={"chat_template_kwargs": {
#         "enable_thinking": False
#     }}
# )

from shared.model import get_model

model = get_model()
# model = LiteLlm(
#     model="ollama_chat/qwen3:8b",
#     extra_body={
#         "think": False,
#     }
# )

# model = LiteLlm(
#     model="ollama_chat/qwen3:8b",
#     model_kwargs={
#         "chat_template_kwargs": {
#             # "enable_thinking": False
#             "think": False,
#         }
#     }
# )

logging.info(model)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Orchestrator.",
    instruction=f"""
    Talk to the user.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
