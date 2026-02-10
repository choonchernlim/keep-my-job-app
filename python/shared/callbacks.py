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
