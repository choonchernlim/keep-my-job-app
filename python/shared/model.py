import logging
import os

from google.adk.models import LiteLlm


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

    logging.info(f"Model: {model}")

    return model
