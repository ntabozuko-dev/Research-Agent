from agents.base_agent import BaseAgent
from tools.web_search import web_search

TOOLS = [
    {
        'name': 'web_search',
        'description': 'Search the web for information on a topic.',
        'params': '{"query": "string"}'
    }
]


class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name='SearchAgent',
            system_prompt=(
                'You are a research search specialist. '
                'When given a research topic, formulate a good search query '
                'and call the web_search tool.'
            ),
            tools=TOOLS
        )

    def run(self, topic: str) -> list[dict]:
        """Search for a topic and return result list."""
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': f'Find information about: {topic}'}
        ]
        reply = self._chat(messages)
        tool_call = self._parse_tool_call(reply)
        if tool_call and tool_call['tool'] == 'web_search':
            query = tool_call['args'].get('query') or topic
            print(f'  [SearchAgent] Calling web_search("{query}")')
            return web_search(query)
        # Fallback: model did not use the tool, search directly
        print(f'  [SearchAgent] Fallback direct search for: {topic}')
        return web_search(topic)
