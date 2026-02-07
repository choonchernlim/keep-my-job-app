import logging

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


def set_c4_field_to_state_tool(
        tool_context: ToolContext,
        key: int,
        field: str,
        value: str) -> dict[str, str]:
    logging.info(f"##### : key={key}, field={field}, value={value}...")
    tool_context.state["c4"] = tool_context.state.get("c4", {})

    if key not in tool_context.state["c4"]:
        tool_context.state["c4"][key] = {}

    tool_context.state["c4"][key][field] = value

    return {"status": "success"}


def get_next_c4_from_state_tool(
        tool_context: ToolContext,
        missing_field: str) -> dict[str, str] | None:
    logging.info(f"##### : missing_field={missing_field}...")
    tool_context.state["c4"] = tool_context.state.get("c4", {})

    for key, info in tool_context.state["c4"].items():
        if missing_field not in info:
            return {
                "key": key,
                "diagram_type": info["diagram_type"],
                "description": info["description"],
            }

    return None
