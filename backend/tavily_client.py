import json
import logging
import requests
from typing import Dict, Any, List
from backend.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)

class TavilyClient:
    """
    Client for interacting with the Tavily AI Search API.
    Used for real-time web grounding, deep fact-retrieval, and automated intelligence gathering.
    """
    BASE_URL = "https://api.tavily.com"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or TAVILY_API_KEY
        if not self.api_key:
            logger.warning("TAVILY_API_KEY is not set. Real-time web search will be disabled.")

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 5,
        include_answer: bool = True,
        include_raw_content: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes an advanced AI-optimized search query.
        """
        if not self.api_key:
            return {
                "answer": "Tavily API key is missing. Please configure TAVILY_API_KEY in .env.",
                "results": [],
                "query": query
            }

        endpoint = f"{self.BASE_URL}/search"
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            return {
                "answer": data.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0.0),
                    }
                    for r in data.get("results", [])
                ],
                "query": query
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error querying Tavily API: {e}")
            return {
                "error": str(e),
                "answer": "",
                "results": [],
                "query": query
            }
