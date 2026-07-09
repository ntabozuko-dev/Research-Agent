from agents.base_agent import BaseAgent

class FactCheckerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name='FactCheckerAgent',
            system_prompt=(
                'You are a fact-checking expert. '
                'Given a summary, identify any statements that may be incorrect, misleading, or unsupported. '
                'Return your findings as bullet points. If everything seems correct, say so clearly.'
            ),
            tools=[]
        )

    def run(self, summary: str) -> str:
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'user', 'content': f'Fact-check this summary:\n\n{summary}'}
        ]
        response = self._chat(messages)
        return response['message']['content']