"""Autonomous Research Agent - Monitors topics and summarizes news.

This agent runs continuously, monitors specified topics across the web,
and automatically summarizes new information.
"""

import asyncio
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from dino_os.agent_core import Agent
from dino_os.memory_layer import MemoryLayer


class AutonomousResearcherAgent(Agent):
    """Autonomous agent that monitors topics and summarizes news.
    
    Runs continuously, checks for new information on watched topics,
    and generates summaries automatically.
    """
    
    name = "autoresearcher"
    description = "Autonomous: Monitors topics and summarizes news automatically"
    
    def __init__(self):
        super().__init__()
        self.memory = MemoryLayer()
        self.watched_topics: List[str] = []
        self.check_interval = 300  # Check every 5 minutes
        self.is_running = False
        self.last_check: Dict[str, datetime] = {}
        
    def add_topic(self, topic: str):
        """Add a topic to monitor."""
        self.watched_topics.append(topic)
        print(f"   📚 Added topic: {topic}")
        
    async def run(self):
        """Start autonomous research loop."""
        self.is_running = True
        
        if not self.watched_topics:
            # Default topics
            self.watched_topics = ["AI", "Python", "Technology"]
            
        print(f"🔬 Autonomous Researcher started")
        print(f"   Watching {len(self.watched_topics)} topics")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while self.is_running:
                await self._research_all_topics()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n🛑 Autonomous Researcher stopped")
            
        return {"status": "success", "output": "Research cycle completed"}
    
    async def _research_all_topics(self):
        """Research all watched topics."""
        for topic in self.watched_topics:
            await self._research_topic(topic)
            await asyncio.sleep(5)  # Be nice to search engines
    
    async def _research_topic(self, topic: str):
        """Research a specific topic."""
        now = datetime.now()
        
        # Check if we should search this topic (avoid duplicates)
        last_time = self.last_check.get(topic)
        if last_time and (now - last_time) < timedelta(minutes=5):
            return
            
        print(f"🔍 Researching: {topic}")
        
        try:
            results = await self._search_web(topic)
            
            if results:
                summary = self._generate_summary(topic, results)
                
                # Store in memory
                memory_key = f"research_{topic}_{now.strftime('%Y%m%d_%H%M')}"
                self.memory.add(memory_key, json.dumps({
                    'topic': topic,
                    'timestamp': now.isoformat(),
                    'summary': summary,
                    'results_count': len(results)
                }))
                
                print(f"   ✅ Found {len(results)} results")
                print(f"   📝 Summary saved to memory: {memory_key}")
                
                # Check for significant news
                if self._is_significant_news(results):
                    print(f"   🚨 Significant news detected for {topic}!")
                    await self._alert_user(topic, summary)
                    
            self.last_check[topic] = now
            
        except Exception as e:
            print(f"   ❌ Research error: {e}")
    
    async def _search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search the web for information."""
        try:
            # Use DuckDuckGo HTML
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(search_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                html = response.read().decode('utf-8')
            
            # Parse results
            results = []
            
            # Extract titles and snippets
            title_pattern = r'<a[^>]+class="result__a"[^>]*>(.*?)</a>'
            snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>'
            
            titles = re.findall(title_pattern, html)[:max_results]
            snippets = re.findall(snippet_pattern, html)[:max_results]
            
            for i, (title, snippet) in enumerate(zip(titles, snippets)):
                # Clean HTML
                title = re.sub(r'<[^>]+>', '', title)
                snippet = re.sub(r'<[^>]+>', '', snippet)
                
                results.append({
                    'title': title,
                    'snippet': snippet,
                    'timestamp': datetime.now().isoformat()
                })
            
            return results
            
        except Exception as e:
            print(f"   Search error: {e}")
            return []
    
    def _generate_summary(self, topic: str, results: List[Dict]) -> str:
        """Generate a summary of research results."""
        summary = f"Research Summary: {topic}\n"
        summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        summary += "=" * 50 + "\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result['title']}\n"
            summary += f"   {result['snippet'][:200]}...\n\n"
        
        return summary
    
    def _is_significant_news(self, results: List[Dict]) -> bool:
        """Determine if results contain significant news."""
        # Simple heuristic: check for breaking/urgent keywords
        significant_keywords = ['breaking', 'urgent', 'major', 'announced', 'launched', 'released']
        
        for result in results:
            text = (result.get('title', '') + ' ' + result.get('snippet', '')).lower()
            if any(keyword in text for keyword in significant_keywords):
                return True
        
        return False
    
    async def _alert_user(self, topic: str, summary: str):
        """Alert user about significant news."""
        print(f"\n{'='*60}")
        print(f"🚨 SIGNIFICANT NEWS ALERT: {topic}")
        print(f"{'='*60}")
        print(summary[:500])
        print(f"{'='*60}\n")
        
        # Could also send notifications, emails, etc.
    
    def get_research_history(self, topic: Optional[str] = None) -> List[Dict]:
        """Get research history from memory."""
        results = []
        
        if topic:
            # Search for specific topic
            keys = self.memory.list_keys(prefix=f"research_{topic}")
        else:
            # Get all research
            keys = self.memory.list_keys(prefix="research_")
        
        for key in keys:
            entry = self.memory.get(key)
            if entry:
                try:
                    data = json.loads(entry['value'])
                    results.append(data)
                except:
                    pass
        
        return sorted(results, key=lambda x: x.get('timestamp', ''), reverse=True)
    
    def generate_report(self, days: int = 7) -> str:
        """Generate a research report for the last N days."""
        history = self.get_research_history()
        
        cutoff = datetime.now() - timedelta(days=days)
        recent = [h for h in history if datetime.fromisoformat(h['timestamp']) > cutoff]
        
        report = f"Research Report (Last {days} days)\n"
        report += "=" * 60 + "\n\n"
        
        for entry in recent:
            report += f"Topic: {entry['topic']}\n"
            report += f"Time: {entry['timestamp']}\n"
            report += f"Results: {entry['results_count']}\n"
            report += "-" * 40 + "\n"
            report += entry['summary'][:300] + "...\n\n"
        
        return report
    
    def stop(self):
        """Stop autonomous operation."""
        self.is_running = False
        print("\n🛑 Stopping Autonomous Researcher...")


if __name__ == "__main__":
    # Run autonomously
    agent = AutonomousResearcherAgent()
    agent.add_topic("Artificial Intelligence")
    agent.add_topic("Python Programming")
    asyncio.run(agent.run())
