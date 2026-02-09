import logging
from typing import Any

from google.adk.tools import ToolContext


# def append_to_state_tool(
#         tool_context: ToolContext,
#         field: str,
#         response: str) -> dict[str, str]:
#     """Append new output to an existing state key.
#
#     Args:
#         :param tool_context: tool context
#         :param field: a field name to append to
#         :param response: a string to append to the field
#
#     Returns:
#         dict[str, str]: {"status": "success"}
#     """
#     # list all fields in the state for debugging
#
#     existing_state = tool_context.state.get(field, [])
#     tool_context.state[field] = existing_state + [response]
#     logging.info(f"[Added to {field}] {response}")
#
#     logging.info(f"[########] {tool_context.state.to_dict()}")
#
#     return {"status": "success"}


# def set_c4_to_state_tool(
#         tool_context: ToolContext,
#         key: int,
#         diagram_type: str,  # context or container
#         description: str,
#         mermaid_syntax: str = None) -> dict[str, str]:
#     logging.info(
#         f"##### : key={key}, diagram_type={diagram_type}, description={description}, mermaid_syntax={mermaid_syntax}...")
#
#     tool_context.state["c4"] = tool_context.state.get("c4", {})
#     tool_context.state["c4"][key] = {
#         "diagram_type": diagram_type,
#         "description": description,
#         "mermaid_syntax": mermaid_syntax,
#     }
#
#     return {"status": "success"}

def set_state_tool(
        tool_context: ToolContext,
        field: str,
        value: str) -> None:
    logging.info(f"##### : field={field}, value={value}...")

    tool_context.state[field] = value


def get_state_tool(
        tool_context: ToolContext,
        field: str) -> str:
    logging.info(f"##### : field={field}...")

    if field not in tool_context.state:
        raise ValueError(f"Field [{field}] not found in state.")

    return tool_context.state[field]


def get_c4_by_key_tool(
        tool_context: ToolContext,
        key: int) -> dict[str, str]:
    logging.info(f"##### : key={key}...")
    tool_context.state["c4"] = tool_context.state.get("c4", {})

    if key not in tool_context.state["c4"]:
        raise ValueError(f"C4 with key [{key}] not found in state.")

    return tool_context.state["c4"][key]


def set_c4_field_to_state_tool(
        tool_context: ToolContext,
        key: int,
        field: str,
        value: str) -> None:
    """
    Set a specific field of a C4 diagram in the state. If the C4 diagram with the given key does not exist, it will be created.

    :param tool_context: Tool context
    :param key: Unique identifier for the C4 diagram (e.g., 1, 2, 3)
    :param field: Field name to set (e.g., diagram_type, description, mermaid_syntax)
    :param value: Value to set for the specified field
    :return: {"status": "success"}
    """
    logging.info(f"##### : key={key}, field={field}, value={value}...")

    state = tool_context.state.setdefault("c4", {})
    state.setdefault(key, {})[field] = value


# def get_next_c4_from_state_tool(
#         tool_context: ToolContext,
#         missing_field: str) -> dict[str, Any] | None:
#     logging.info(f"##### : missing_field={missing_field}...")
#     tool_context.state["c4"] = tool_context.state.get("c4", {})
#
#     for key, info in tool_context.state["c4"].items():
#         if missing_field not in info:
#             return {
#                 "key": key,
#                 "diagram_type": info["diagram_type"],
#                 "description": info["description"],
#                 "processed": False,
#             }
#
#     return None


def set_new_c4_request_tool(
        tool_context: ToolContext,
        diagram_type: str,
        description: str) -> dict[str, str]:
    logging.info(f"##### : diagram_type={diagram_type}, description={description}...")

    state = tool_context.state.setdefault("c4", {})

    # count items in state to determine the new key
    key = len(state) + 1

    # new request
    state[key] = {
        "key": key,
        "diagram_type": diagram_type,
        "description": description,
        "processed": False,
    }

    return {
        **{"status": "success"},
        **state[key]
    }


def save_processed_c4_request_tool(
        tool_context: ToolContext,
        key: int,
        mermaid_syntax: str) -> dict[str, str]:
    logging.info(f"#####...")

    state = tool_context.state.get("c4")
    state[key]["processed"] = True
    state[key]["mermaid_syntax"] = mermaid_syntax

    return {
        "status": "success",
    }


def get_next_unprocessed_c4_request_tool(
        tool_context: ToolContext):
    logging.info(f"#####...")

    state = tool_context.state.get("c4")

    return next(({
        "status": "success",
        "key": info["key"],
        "diagram_type": info["diagram_type"],
        "description": info["description"],
    } for info in state.values() if not info["processed"]), {"status": "not_found"})

    # if request:
    #     return {
    #         "status": "success",
    #         "key": request["key"],
    #         "diagram_type": request["diagram_type"],
    #         "description": request["description"],
    #     }
    #
    # return {
    #     "status": "not_found",
    # }

    # for info in tool_context.state["c4"].values():
    #     if not info["processed"]:
    #         return info
    #
    # return None
