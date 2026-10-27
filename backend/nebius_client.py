import os
import json
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from backend.config import NEBIUS_API_KEY, NEBIUS_BASE_URL, NEBIUS_MODEL

logger = logging.getLogger(__name__)

class NebiusNemotronClient:
    """
    Client for Nebius Token Factory hosting NVIDIA Nemotron models.
    Default Model: nvidia/llama-3.1-nemotron-70b-instruct
    Endpoint: https://api.tokenfactory.nebius.com/v1/
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or NEBIUS_API_KEY
        self.base_url = base_url or NEBIUS_BASE_URL
        self.model = model or NEBIUS_MODEL
        
        self.is_configured = bool(self.api_key and self.api_key != "your_nebius_api_key_here")
        
        if self.is_configured:
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        else:
            self.client = None
            logger.info("Nebius API key not yet configured. Running in hybrid/simulation mode for testing.")

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 2500,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Sends a chat completion request to Nebius Token Factory for Nemotron-70B.
        """
        if not self.is_configured:
            # High-fidelity synthesis fallback when waiting for Nebius key activation
            return self._fallback_synthesis(messages)

        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling Nebius Token Factory ({self.model}): {e}")
            raise e

    def _fallback_synthesis(self, messages: List[Dict[str, str]]) -> str:
        """
        Fallback response for local dry-run before Nebius API key is inserted.
        """
        user_msg = messages[-1]["content"] if messages else ""
        return (
            "### [Nebius Token Factory Simulation Mode]\n"
            "*Notice: Add your NEBIUS_API_KEY in .env to activate live NVIDIA Nemotron-70B inference on Nebius Token Factory.*\n\n"
            f"Synthesizing input:\n{user_msg[:300]}..."
        )
