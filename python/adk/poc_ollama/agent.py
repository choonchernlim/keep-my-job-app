import os
import logging
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.models import LiteLlm
from google.genai import types

load_dotenv()

model = LiteLlm(model=os.getenv("MODEL")) if os.getenv("LITELLM") else os.getenv("MODEL")
logging.info(model)

root_agent = Agent(
    name="root_agent",
    model=model,
    description="Root",
    instruction=f"""
    Talk to user.
    """,
    generate_content_config=types.GenerateContentConfig(temperature=0),
)
