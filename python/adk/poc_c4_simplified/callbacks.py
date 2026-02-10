import json
import logging
from typing import Dict, Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.genai.types import Content


def display_state(callback_context: CallbackContext, color: str, label: str, value: str) -> Optional[Dict]:
    state = callback_context.state.to_dict()

    # if some of the state values are longer than 200 characters, truncate them for better readability in logs
    for key, value in state.items():
        if isinstance(value, str) and len(value) > 200:
            state[key] = value[:200] + "...(truncated)"

    formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)
    logging.info(f"""{color}
################################################
[Callback] {label}: {value}
################################################
{formatted_state}
    \033[0m""")


def display_tool_state(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
) -> Optional[Dict]:
    display_state(tool_context, "\033[96m", "Tool", tool.name)


#     state = tool_context.state.to_dict()
#
#     # if some of the state values are longer than 200 characters, truncate them for better readability in logs
#     for key, value in state.items():
#         if isinstance(value, str) and len(value) > 200:
#             state[key] = value[:200] + "...(truncated)"
#
#     formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)
#     logging.info(f"""\033[96m
# ################################################
# [Callback] Tool: {tool.name}
# ################################################
# {formatted_state}
#     \033[0m""")


def display_agent_state(callback_context: CallbackContext) -> Optional[Content]:
    display_state(callback_context, "\033[94m", "Agent", callback_context.agent_name)

#     agent_name = callback_context.agent_name
#     state = callback_context.state.to_dict()
#
#     # if some of the state values are longer than 200 characters, truncate them for better readability in logs
#     for key, value in state.items():
#         if isinstance(value, str) and len(value) > 200:
#             state[key] = value[:200] + "...(truncated)"
#
#     formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)
#
#     logging.info(f"""\033[94m
# ################################################
# [Callback] Agent: {agent_name}
# ################################################
# {formatted_state}
#     \033[0m""")
