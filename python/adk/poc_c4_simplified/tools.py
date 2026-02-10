import logging
from datetime import datetime
from pathlib import Path

from google.adk.tools import ToolContext
from google.genai.types import Part

DATA_PATH = Path.cwd().parent.parent / "data"

# fail if data path does not exist
if not DATA_PATH.exists():
    raise ValueError(f"Data path [{DATA_PATH}] does not exist.")


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


def save_new_c4_request_tool(
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
    state = tool_context.state.get("c4")
    state[key]["processed"] = True
    state[key]["mermaid_syntax"] = mermaid_syntax

    tool_context.state.update({
        "key": None,
        "diagram_type": None,
        "description": None,
        "mermaid_syntax": None,
        "png_filename": None,
        "png_directory_path": None,
    })

    return {
        "status": "success",
    }

    # return next(({
    #     "status": "success",
    #     "key": info["key"],
    #     "diagram_type": info["diagram_type"],
    #     "description": info["description"],
    # } for info in state.values() if not info["processed"]), {"status": "not_found"})


def get_next_unprocessed_c4_request_tool(
        tool_context: ToolContext):
    state = tool_context.state.get("c4")

    request = next((info for info in state.values() if not info["processed"]), None)

    if request:
        tool_context.state.update({
            "key": request["key"],
            "diagram_type": request["diagram_type"],
            "description": request["description"],
            "mermaid_syntax": None,
            "png_filename": f"{datetime.now().strftime('%Y%m%d%H%M')}__{request["key"]}__{request["diagram_type"]}.png",
            "png_directory_path": str(DATA_PATH / "images"),
        })

        return {
            "status": "success",
            "key": request["key"],
            "diagram_type": request["diagram_type"],
            "description": request["description"],
        }

    return {
        "status": "not_found",
    }


async def save_png_file_as_artifact_tool(
        tool_context: ToolContext,
        png_filename: str,
        png_directory_path: str,
) -> dict[str, str]:
    with open(Path(png_directory_path) / f"{png_filename}", "rb") as f:
        image_data = f.read()

    image = Part.from_bytes(
        data=image_data,
        mime_type="image/png",
    )

    version = await tool_context.save_artifact(png_filename, image)

    return {
        "status": "success",
        "version": version,
    }

    # for info in tool_context.state["c4"].values():
    #     if not info["processed"]:
    #         return info
    #
    # return None

# async def save_png_file_as_artifact_tool(
#         tool_context: ToolContext,
#         png_directory_path: str,
# ) -> dict[str, str]:
#     # 1. FIX: Derive the filename from the path (or pass it as an argument)
#     filename = os.path.basename(png_directory_path)
#
#     # 2. FIX: Read the actual bytes from the file
#     # Part.from_bytes expects 'bytes', not a string path
#     with open(png_directory_path, "rb") as f:
#         image_data = f.read()
#
#     image = Part.from_bytes(
#         data=image_data,
#         mime_type=mime_type,
#     )
#
#     # 3. Save using the defined filename and the byte content
#     version = await tool_context.save_artifact(filename, image)
#
#     return {"status": "success", "version": version}
