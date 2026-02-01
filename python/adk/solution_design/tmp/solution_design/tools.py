import logging
import os

from google.adk.tools import ToolContext


# def get_question(num):
#     with open(f"solution_design/questions/{num}.txt", "r") as f:
#         question = f.read()
#
#     return question


def append_to_state_tool(
        tool_context: ToolContext,
        field: str,
        response: str) -> dict[str, str]:
    """Append new output to an existing state key.

    Args:
        :param tool_context: tool context
        :param field: a field name to append to
        :param response: a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    existing_state = tool_context.state.get(field, [])
    tool_context.state[field] = existing_state + [response]
    logging.info(f"[Added to {field}] {response}")

    return {"status": "success"}


def save_to_state_tool(
        tool_context: ToolContext,
        field: str,
        response: str) -> dict[str, str]:
    """Set output to a state key.

    Args:
        :param tool_context: tool context
        :param field: a field name to save to
        :param response: a string to append to the field

    Returns:
        dict[str, str]: {"status": "success"}
    """
    tool_context.state[field] = response
    logging.info(f"[Added to {field}] {response}")

    return {"status": "success"}


# def load_question_into_state_tool(tool_context: ToolContext, number: int) -> dict[str, str]:
#     """Load a question from file into tool context state.
#
#     Args:
#         :param tool_context: tool context
#         :param number: question number to load from file, ex: 1 => 1.txt
#
#     Returns:
#         dict[str, str]: {"status": "success"}
#     """
#     with open(f"solution_design/questions/{number}.txt", "r") as f:
#         question = f.read()
#
#     tool_context.state["QUESTION"] = question
#
#     return {"status": "success"}

def load_problem_into_state_tool(
        tool_context: ToolContext,
        directory: str,
        number: int,
        field: str,
) -> dict[str, str]:
    """Load a problem from file into tool context state.

    Args:
        :param tool_context: tool context
        :param directory: directory where question files are stored
        :param number: problem number to load from file, ex: 1 => 1.txt
        :param field: a field name to save to
    Returns:
        dict[str, str]: {"status": "success"}
    """

    target_path = os.path.join(directory, f"{number}.txt")

    with open(target_path, "r") as f:
        save_to_state_tool(tool_context, field, f.read())

    return {"status": "success"}
