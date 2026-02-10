import json
import logging
from typing import Dict, Any, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import BaseTool, ToolContext
from google.genai.types import Content


def display_tool_state(
        tool: BaseTool,
        args: Dict[str, Any],
        tool_context: ToolContext
) -> Optional[Dict]:
    state = tool_context.state.to_dict()
    formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)
    logging.info(f"""\033[96m
################################################
[Callback] Tool: {tool.name}
################################################
{formatted_state}
    \033[0m""")


def display_agent_state(callback_context: CallbackContext) -> Optional[Content]:
    agent_name = callback_context.agent_name
    state = callback_context.state.to_dict()
    formatted_state = json.dumps(state, indent=4, sort_keys=True, default=str)

    logging.info(f"""\033[94m
################################################
[Callback] Agent: {agent_name}
################################################
{formatted_state}
    \033[0m""")
