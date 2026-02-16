"""Web Search Agent - Search the web for information."""

import asyncio
import json
from dino_os.agent_core import Agent
import urllib.request
import urllib.parse


class WebSearchAgent(Agent):
    """Agent that can search the web for information."""
    
    name = "websearch"
    description = "Searches the web for information"
    
    async def run(self, query: str = None):
        """Run web search."""
        if query is None:
            return {
                "status": "success", 
                "output": "Web search agent ready. Pass a query to search."
            }
        
        try:
            # Use DuckDuckGo HTML version (no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(search_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                
            # Extract titles and snippets (basic parsing)
            results = []
            # Look for result links
            import re
            links = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', html)
            snippets = re.findall(r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', html)
            
            for i, (title, snippet) in enumerate(zip(links[:5], snippets[:5])):
                # Clean HTML tags
                title = re.sub(r'<[^>]+>', '', title)
                snippet = re.sub(r'<[^>]+>', '', snippet)
                results.append(f"{i+1}. {title}\n   {snippet}\n")
            
            if results:
                output = f"Search results for '{query}':\n\n" + "\n".join(results)
            else:
                output = f"No results found for '{query}'"
                
            return {
                "status": "success",
                "output": output
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Search failed: {e}"
            }
