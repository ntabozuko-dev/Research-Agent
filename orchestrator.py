from agents.search_agent import SearchAgent
from agents.summariser_agent import SummariserAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.citation_agent import CitationAgent
from llm import OllamaError


class ResearchOrchestrator:
    def __init__(self):
        print('Initialising agents...')
        self.search_agent = SearchAgent()
        self.summariser_agent = SummariserAgent()
        self.fact_checker_agent = FactCheckerAgent()
        self.citation_agent = CitationAgent()
        print('All agents ready.\n')

    def run(self, query: str) -> str:
        print(f'Orchestrator received query: "{query}"\n')
        try:
            print('[Step 1] Dispatching SearchAgent...')
            results = self.search_agent.run(query)
            if not results:
                return 'No results found. Try a different query.'
            print(f'  Found {len(results)} results.\n')

            print('[Step 2] Dispatching SummariserAgent...')
            combined_text = ' '.join(r.get('snippet', '') for r in results)
            summary = self.summariser_agent.run(combined_text)
            print('  Summary complete.\n')

            print('[Step 3] Dispatching FactCheckerAgent...')
            fact_check = self.fact_checker_agent.run(summary)
            print('  Fact-check complete.\n')

            print('[Step 4] Dispatching CitationAgent...')
            citations = self.citation_agent.run(results)
            print('  Citations formatted.\n')

            return self._compile_report(query, summary, fact_check, citations)

        except OllamaError as e:
            return f'The research pipeline could not reach the language model. {e}'
        except Exception as e:
            return (
                'The research pipeline encountered a problem and could not '
                f'complete. Error: {e}'
            )

    def _compile_report(self, query, summary, fact_check, citations):
        lines = [
            'RESEARCH REPORT',
            f'Query: {query}',
            '=' * 50,
            '',
            'SUMMARY',
            '-' * 30,
            summary,
            '',
            'FACT CHECK',
            '-' * 30,
            fact_check,
            '',
            'SOURCES',
            '-' * 30,
        ]
        for i, c in enumerate(citations, 1):
            lines.append(f'[{i}] {c}')
        return '\n'.join(lines)
