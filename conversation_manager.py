from llm import chat, OllamaError
from orchestrator import ResearchOrchestrator
from tool_parsing import parse_tool_call

# Describe the orchestrator as a tool the LLM can call
RESEARCH_TOOL = {
    'name': 'run_research',
    'description': (
        'Search the web for a topic, summarise the findings, '
        'and return a formatted report with citations. '
        'Call this whenever the user asks you to research something.'
    ),
    'params': '{"topic": "string"}'
}

SYSTEM_PROMPT = """You are a helpful research assistant.
You can answer general questions in plain conversation.
When the user explicitly asks you to research a topic — for example
by saying 'research X', 'look up X', or 'find information about X' —
you MUST respond with ONLY the following JSON and nothing else:
  {"tool": "run_research", "args": {"topic": "<topic>"}}
Do NOT use the tool for casual conversation or simple factual questions.
Only use it when the user clearly wants a research report."""


class ConversationManager:
    def __init__(self):
        self.orchestrator = ResearchOrchestrator()
        self.history = []

    def system_message(self) -> dict:
        tool_desc = (
            f'\n\nAvailable tool:\n'
            f'  - {RESEARCH_TOOL["name"]}: {RESEARCH_TOOL["description"]}\n'
            f'    Parameters: {RESEARCH_TOOL["params"]}'
        )
        return {'role': 'system', 'content': SYSTEM_PROMPT + tool_desc}

    def _build_messages(self, user_input: str) -> list[dict]:
        """Build the full message list: system + history + new user message."""
        return [self.system_message()] + self.history + [
            {'role': 'user', 'content': user_input}]

    def send(self, user_input: str) -> str:
        """
        Send a user message, handle any tool call, and return
        the final assistant reply to display to the user.
        """
        messages = self._build_messages(user_input)
        try:
            reply = chat(messages)
            tool_call = parse_tool_call(reply)

            if tool_call and tool_call['tool'] == 'run_research':
                topic = tool_call['args'].get('topic') or user_input
                print(f'\n[ConversationManager] Research triggered for: "{topic}"')

                # Run the full research pipeline
                report = self.orchestrator.run(topic)

                # Inject the report back into the conversation
                # so the model can respond naturally to it
                messages.append({'role': 'assistant', 'content': reply})
                messages.append({'role': 'user',
                                 'content': f'Here are the research results:\n\n{report}'})
                final_reply = chat(messages)

                # If the model emitted another tool call instead of prose,
                # fall back to showing the report itself.
                if parse_tool_call(final_reply):
                    final_reply = report
                reply = final_reply
        except OllamaError as e:
            # Connection problems are reported, but not stored in the history.
            return str(e)

        self.history.append({'role': 'user', 'content': user_input})
        self.history.append({'role': 'assistant', 'content': reply})
        return reply
