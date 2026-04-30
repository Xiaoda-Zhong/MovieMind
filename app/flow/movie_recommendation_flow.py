# app/flow/movie_recommendation_flow.py
import asyncio
import json
from typing import Dict, Any, Optional
from app.agent.base import BaseAgent
from app.flow.base import BaseFlow
from app.logger import logger

class MovieRecommendationFlow(BaseFlow):
    """
    A custom workflow that:
    1. Interprets user's movie request (e.g., "Recommend an action movie")
    2. Uses the movie recommendation tool to find movies by genre
    3. Optionally fetches details for a selected movie
    """

    def __init__(self, agents: Dict[str, BaseAgent], **kwargs):
        super().__init__(agents, **kwargs)
        self.primary_agent_key = "manus"

    async def execute(self, input_text: str) -> str:
        """Main entry point for the flow."""
        logger.info(f"MovieRecommendationFlow started with input: {input_text}")
        primary_agent = self.agents.get(self.primary_agent_key)
        if not primary_agent:
            return "Error: Primary agent 'manus' not found in agents dictionary."

        # Step 1: Determine user's intent and extract parameters
        intent = await self._determine_intent(primary_agent, input_text)
        if not intent:
            return "Could not determine what you're looking for. Please specify a movie title, genre, or search term."

        # Step 2: Perform the appropriate action based on intent
        if intent.get("action") == "recommend":
            result = await self._get_recommendations(primary_agent, intent.get("genre", "popular"))
        elif intent.get("action") == "search":
            result = await self._search_movies(primary_agent, intent.get("query", input_text))
        elif intent.get("action") == "details":
            result = await self._get_movie_details(primary_agent, intent.get("title", input_text))
        else:
            result = "I'm not sure how to help with that request. Try asking for movie recommendations by genre or searching for a specific movie."

        return result

    async def _determine_intent(self, agent: BaseAgent, user_input: str) -> Optional[Dict[str, Any]]:
        """Use the LLM to analyze user intent and extract relevant parameters."""
        prompt = f"""
        Analyze the following user request about movies and determine the appropriate action.
        Output a JSON object with the following structure:
        - For recommendations: {{"action": "recommend", "genre": "genre_name"}}
        - For search: {{"action": "search", "query": "search_term"}}
        - For movie details: {{"action": "details", "title": "movie_title"}}
        - If unclear: {{"action": "unknown"}}

        User request: "{user_input}"

        Genre should be one of: action, adventure, animation, comedy, crime, documentary, drama, family, fantasy, history, horror, music, mystery, romance, science_fiction, thriller, tv_movie, war, western.

        Output only the JSON object, no additional text.
        """
        response = await agent.run(prompt)
        try:
            # Clean the response to ensure it's valid JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            intent = json.loads(response.strip())
            return intent
        except json.JSONDecodeError:
            logger.error(f"Failed to parse intent JSON: {response}")
            return None

    async def _get_recommendations(self, agent: BaseAgent, genre: str) -> str:
        """Get movie recommendations based on genre."""
        prompt = f"Use the movie_recommendation tool with action='recommend' and genre='{genre}' to get movie recommendations."
        return await agent.run(prompt)

    async def _search_movies(self, agent: BaseAgent, query: str) -> str:
        """Search for movies by title."""
        prompt = f"Use the movie_recommendation tool with action='search' and query='{query}' to find movies."
        return await agent.run(prompt)

    async def _get_movie_details(self, agent: BaseAgent, title: str) -> str:
        """Get detailed information about a specific movie."""
        prompt = f"Use the movie_recommendation tool with action='details' and query='{title}' to get movie details."
        return await agent.run(prompt)
