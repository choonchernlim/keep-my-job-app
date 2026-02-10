import markdown
from google.adk.tools import ToolContext
from google.genai.types import Part

from shared.utils import get_data_dir_path


def set_state_tool(
        tool_context: ToolContext,
        field: str,
        response: str) -> dict[str, str]:
    """Set a state key to a new value.

    Args:
        :param tool_context: tool context
        :param field: a field name to append to
        :param response: a string to set the field to

    Returns:
        dict[str, str]: {"status": "success"}
    """
    tool_context.state.setdefault(field, response)

    return {"status": "success"}


def get_state_tool(
        tool_context: ToolContext,
        field: str) -> str:
    """Get the value of a state key.

    :param tool_context: tool context
    :param field: field value to get from state
    :return: Field value from state
    """
    if field not in tool_context.state:
        raise ValueError(f"Field [{field}] not found in state.")

    return tool_context.state[field]


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

    return {"status": "success"}


def load_file_data_into_state_tool(
        tool_context: ToolContext,
        directory: str,
        filename: str,
        field: str,
) -> dict[str, str]:
    """Load a file from data directory into tool context state.

    Args:
        :param tool_context: tool context
        :param directory: directory where files are stored
        :param filename: filename to load, ex: filename.txt
        :param field: a field name to save to
    Returns:
        dict[str, str]: {"status": "success"}
    """

    target_path = get_data_dir_path() / directory / filename

    with open(target_path, "r") as f:
        set_state_tool(tool_context, field, f.read())

    return {"status": "success"}


async def save_markdown_content_as_artifact_tool(
        tool_context: ToolContext,
        directory: str,
        filename: str,
        content: str,
) -> dict[str, str]:
    """Save Markdown content as an artifact.

    Args:
        :param tool_context: tool context
        :param directory: directory to save file in
        :param filename: filename to save as
        :param content: data to write to file
    Returns:
        dict[str, str]: {"status": "success"}
    """
    target_path = get_data_dir_path() / directory / filename

    with open(target_path, "w") as f:
        f.write(content)

    html = markdown.markdown(content)

    artifact = Part.from_bytes(
        data=html.encode("utf-8"),
        mime_type="text/html"
    )
    version = await tool_context.save_artifact(f"{filename}.html", artifact)

    return {
        "status": "success",
        "version": version
    }
