import os
import logging
from typing import Dict, Any, List, Optional
from backend.config import TAVILY_API_KEY

logger = logging.getLogger(__name__)

class TavilyGroundingClient:
    """
    Production-grade Tavily AI Search integration.
    Provides real-time web retrieval, snippet extraction, and domain-targeted research.
    Supports official tavily-python SDK with direct REST API fallback.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TAVILY_API_KEY
        self.client = None
        
        if self.api_key:
            try:
                from tavily import TavilyClient as OfficialTavilyClient
                self.client = OfficialTavilyClient(api_key=self.api_key)
                logger.info("Tavily Python SDK initialized successfully.")
            except ImportError:
                logger.warning("tavily-python SDK not found, using direct HTTP fallback.")
            except Exception as e:
                logger.warning(f"Error initializing Tavily SDK: {e}. Falling back to REST API.")
        else:
            logger.warning("TAVILY_API_KEY is not configured.")

    def search(
        self,
        query: str,
        search_depth: str = "advanced",
        max_results: int = 4,
        include_answer: bool = True,
        include_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes an AI-optimized grounded search query with error recovery.
        """
        if not self.api_key:
            return {
                "answer": "Tavily API key is missing. Please set TAVILY_API_KEY in .env.",
                "results": [],
                "query": query
            }

        # Try using the official SDK first
        if self.client:
            try:
                kwargs = {
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_answer": include_answer,
                }
                if include_domains:
                    kwargs["include_domains"] = include_domains

                response = self.client.search(**kwargs)
                return {
                    "answer": response.get("answer", ""),
                    "results": [
                        {
                            "title": r.get("title", "Untitled Source"),
                            "url": r.get("url", "#"),
                            "content": r.get("content", ""),
                            "score": round(float(r.get("score", 0.85)), 2),
                        }
                        for r in response.get("results", [])
                    ],
                    "query": query
                }
            except Exception as e:
                logger.warning(f"Official Tavily SDK search failed: {e}. Attempting REST fallback.")

        # REST API Fallback
        import requests
        try:
            payload = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
                "include_answer": include_answer,
            }
            if include_domains:
                payload["include_domains"] = include_domains

            resp = requests.post("https://api.tavily.com/search", json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {
                "answer": data.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", "Untitled Source"),
                        "url": r.get("url", "#"),
                        "content": r.get("content", ""),
                        "score": round(float(r.get("score", 0.85)), 2),
                    }
                    for r in data.get("results", [])
                ],
                "query": query
            }
        except Exception as e:
            logger.error(f"Tavily REST search error: {e}")
            return {
                "error": str(e),
                "answer": "",
                "results": [],
                "query": query
            }
