import logging
import os

from google.adk.models import LiteLlm
from google.adk.models.google_llm import Gemini
from google.genai.types import HttpRetryOptions

def get_model():
    """
    Return the model to use for the agent.

    :return: The model to use for the agent.
    """
    model = os.getenv("MODEL")

    if not model:
        raise ValueError("MODEL env is missing")

    # if model name has a slash, we assume it's in the format of "provider/model_name" and we will use LiteLlm to load it.
    if "/" in model:
        model = LiteLlm(
            model=model,
            extra_body={
                "think": False,  # thinking is too slow
            }
        )
    elif "gemini" in model.lower():
        model = Gemini(
            model=model,
            retry_options=HttpRetryOptions(
                attempts=10,          # Maximum number of retries
                initial_delay=2.0,   # Seconds to wait before the first retry
                exp_base=2.0,        # Exponential backoff multiplier
                max_delay=60.0       # Maximum wait time between retries
            )
        )

    logging.info(f"Model: {model}")

    return model
