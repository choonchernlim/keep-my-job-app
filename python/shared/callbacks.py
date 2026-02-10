import json
import logging
from typing import Dict, Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.genai.types import Content


def _truncate_string(s: str, max_length: int = 100) -> str:
    return s[:max_length] + "...(truncated)" if len(s) > max_length else s


def display_state(
        callback_context: CallbackContext,
        color: str,
        header_label: str,
        header_value: str) -> Optional[Dict]:
    state = callback_context.state.to_dict()

    # if some of the state values are too long, truncate them for better readability in logs
    for key, value in state.items():
        if isinstance(value, str):
            state[key] = _truncate_string(value)
        # if instance is list, ensure each item is a string and truncate if it is too long
        elif isinstance(value, list):
            truncated_list = []
            for item in value:
                if isinstance(item, str) and len(item) > 200:
                    truncated_list.append(_truncate_string(item))
                else:
                    truncated_list.append(item)
            state[key] = truncated_list

    formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)
    logging.info(f"""{color}
################################################
[Callback] {header_label}: {header_value}
################################################
{formatted_state}
    \033[0m""")


# noinspection PyUnusedLocal
def display_tool_state(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
) -> Optional[Dict]:
    display_state(tool_context, "\033[96m", "Tool", tool.name)


def display_agent_state(callback_context: CallbackContext) -> Optional[Content]:
    display_state(callback_context, "\033[94m", "Agent", callback_context.agent_name)

def set_agent_state(data: Dict[str, Any]) -> Any:
    """
    Sets the agent state with the provided data. If any of the values in the data dictionary are callables
    (like functions), they will be executed to get their return value before updating the state.
    This allows for dynamic values (e.g., current timestamp) to be set in the state at the time of execution.

    :param data: Data to set in the agent state. Values can be static or callables that return the value when executed.
    :return: Agent callback function
    """
    async def callback(callback_context: CallbackContext) -> Optional[Content]:
        # We iterate to check for callables (like datetime.now) to ensure
        # the values are fresh for this specific execution
        resolved_data = {}
        for k, v in data.items():
            if callable(v):
                resolved_data[k] = v()  # Execute the function (e.g. get current time)
            else:
                resolved_data[k] = v  # Use static value

        # Update the state
        callback_context.state.update(resolved_data)

    return callback
