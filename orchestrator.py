from agents.search_agent import SearchAgent 
from agents.summariser_agent import SummariserAgent 
from agents.citation_agent import CitationAgent 
from agents.fact_checker_agent import FactCheckerAgent
 
class ResearchOrchestrator: 
    def __init__(self): 
        print('Initialising agents...') 
        self.search_agent     = SearchAgent() 
        self.summariser_agent = SummariserAgent() 
        print('[Step 3] Dispatching FactCheckerAgent...')
        #fact_check = self.fact_checker_agent.run(summary)
        print('  Fact-check complete.\n')
        self.citation_agent   = CitationAgent() 
        self.fact_checker_agent = FactCheckerAgent()
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
    
            print('[Step 3] Dispatching CitationAgent...') 
            citations = self.citation_agent.run(results) 
            print('  Citations formatted.\n') 
            fact_check = self.fact_checker_agent.run(summary)
            return self._compile_report(query, summary, fact_check, citations)
    
        except Exception as e: 
            return ( 
                f'The research pipeline encountered a problem and could not ' 
                f'complete. Error: {e}. ' 
                f'Check that Ollama is running and try again.' 
            )
 
    def _compile_report(self, query, summary, fact_check, citations):
        lines = [
        f'RESEARCH REPORT',
        f'Query: {query}',
        f'=' * 50,
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
