from llm import chat
from tool_parsing import parse_tool_call


class BaseAgent:
    def __init__(self, name: str, system_prompt: str, tools: list[dict]):
        self.name = name
        self.tools = tools  # list of tool description dicts
        self.system_prompt = system_prompt + self._build_tool_prompt()

    def _chat(self, messages: list[dict]) -> str:
        """Return the model's reply text. Raises llm.OllamaError on failure."""
        return chat(messages)

    def _build_tool_prompt(self) -> str:
        """Describe tools to the model in the system prompt."""
        if not self.tools:
            return ''
        lines = ['\n\nYou have access to the following tools.',
                 'To call a tool, respond ONLY with valid JSON in this format:',
                 '{"tool": "<tool_name>", "args": {<key: value>}}',
                 'Available tools:']
        for t in self.tools:
            lines.append(f'  - {t["name"]}: {t["description"]}')
            lines.append(f'    Parameters: {t["params"]}')
        return '\n'.join(lines)

    def _parse_tool_call(self, text: str) -> dict | None:
        """Try to parse the model response as a tool call JSON."""
        return parse_tool_call(text)
