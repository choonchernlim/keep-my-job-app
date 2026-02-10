import logging
from datetime import datetime
from pathlib import Path

from google.adk.tools import ToolContext
from google.genai.types import Part

from shared.utils import get_data_dir_path


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
            "png_directory_path": str(get_data_dir_path() / "images"),
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
