import os
import json
import logging
import google.generativeai as genai
from typing import List, Dict, Any

class AIService:
    """Service for generating DAG structures using LLMs."""

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.logger = logging.getLogger("AIService")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Use a stable version of Gemini
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("AI Service initialized with Gemini API Key")
        else:
            self.model = None
            self.logger.warning("AI Service not initialized: GEMINI_API_KEY missing")

    async def generate_dag(self, prompt: str) -> List[Dict[str, Any]]:
        """Generates a proposed DAG structure from a natural language prompt."""
        if not self.model:
            raise ValueError("AI Service not configured: GEMINI_API_KEY is missing")

        system_instructions = (
            "You are a workflow engineer. Convert the user's natural language description into a "
            "Directed Acyclic Graph (DAG) representation. Output ONLY a raw JSON list of tasks. "
            "Each task must have: 'name' (string), 'priority' (integer 1-10), and "
            "'dependencies' (a list of names of other tasks in the same list). "
            "Ensure the graph is acyclic."
        )

        try:
            response = self.model.generate_content(
                f"{system_instructions}\n\nUser Request: {prompt}"
            )
            text = response.text.strip()
            
            # Remove markdown formatting if present
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
                
            return json.loads(text)
        except Exception as e:
            self.logger.error(f"AI generation failed: {str(e)}")
            raise ValueError(f"Failed to generate DAG: {str(e)}")
