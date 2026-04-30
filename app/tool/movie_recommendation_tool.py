# app/tool/movie_recommendation_tool.py
import aiohttp
import tomllib
from pathlib import Path
from typing import Optional
from app.tool.base import BaseTool
import os

class MovieRecommendationTool(BaseTool):
    name: str = "movie_recommendation"
    description: str = """
    Search for movies, get detailed information, and find recommendations based on genres.
    Use this tool when users ask about movie information, want to search for films, or need movie recommendations.
    """

    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["search", "recommend", "details"],
                "description": "Action to perform: 'search' for finding movies by title, 'recommend' for genre-based recommendations, 'details' for fetching detailed movie info.",
            },
            "query": {
                "type": "string",
                "description": "Search query or movie title for 'search' and 'details' actions. Required for 'search' and 'details'.",
            },
            "genre": {
                "type": "string",
                "description": "Genre for recommendations. Required for 'recommend' action. Available genres: action, adventure, animation, comedy, crime, documentary, drama, family, fantasy, history, horror, music, mystery, romance, science_fiction, thriller, tv_movie, war, western.",
            },
        },
        "required": ["action"],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 1. 优先从环境变量读取
        tmdb_key_env = os.getenv("TMDB_API_KEY")
        omdb_key_env = os.getenv("OMDB_API_KEY")

        # 2. 如果环境变量没有，再从 config.toml 读取
        config_path = Path(__file__).parent.parent.parent / "config" / "config.toml"
        tmdb_key_file = None
        omdb_key_file = None
        if config_path.exists():
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
            movie_config = config.get("movie", {})
            tmdb_key_file = movie_config.get("TMDB_API_KEY")
            omdb_key_file = movie_config.get("OMDB_API_KEY")

        # 3. 决定最终使用的 key（环境变量优先）
        self._tmdb_api_key = tmdb_key_env or tmdb_key_file
        self._omdb_api_key = omdb_key_env or omdb_key_file

        if not self._tmdb_api_key:
            raise ValueError("TMDB_API_KEY not found in environment or config.toml under [movie].")
        if not self._omdb_api_key:
            print("Warning: OMDB_API_KEY not set. Some features may be limited.")
        # # Load API keys from config/config.toml
        # config_path = Path(__file__).parent.parent.parent / "config" / "config.toml"
        # if not config_path.exists():
        #     raise FileNotFoundError(f"Config file not found: {config_path}")

        # with open(config_path, "rb") as f:
        #     config = tomllib.load(f)

        # movie_config = config.get("movie", {})
        # self._tmdb_api_key = movie_config.get("TMDB_API_KEY")
        # self._omdb_api_key = movie_config.get("OMDB_API_KEY")

        # if not self._tmdb_api_key:
        #     raise ValueError("TMDB_API_KEY not found in config.toml under [movie] section.")
        # if not self._omdb_api_key:
        #     print("Warning: OMDB_API_KEY not found in config.toml. Some features may be limited.")

    async def execute(self, action: str, query: str = None, genre: str = None) -> str:
        try:
            if action == "search":
                if not query:
                    return "Error: 'query' parameter is required for 'search' action."
                return await self._search_movies(query)
            elif action == "recommend":
                if not genre:
                    return "Error: 'genre' parameter is required for 'recommend' action."
                return await self._recommend_by_genre(genre)
            elif action == "details":
                if not query:
                    return "Error: 'query' parameter is required for 'details' action."
                return await self._get_movie_details(query)
            else:
                return f"Error: Unsupported action '{action}'."
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def _search_movies(self, query: str) -> str:
        """Search for movies by title using TMDB API."""
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": self._tmdb_api_key,
            "query": query,
            "language": "en-US",
            "page": 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if response.status != 200:
                    return f"Error from TMDB API: {data.get('status_message', 'Unknown error')}"

                results = data.get("results", [])[:5]
                if not results:
                    return f"No movies found for '{query}'."

                output = f"Search results for '{query}':\n"
                for idx, movie in enumerate(results, 1):
                    title = movie.get("title", "N/A")
                    year = movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A"
                    output += f"{idx}. {title} ({year})\n"
                return output.strip()

    async def _recommend_by_genre(self, genre: str) -> str:
        """Get popular movie recommendations for a specific genre using TMDB API."""
        genre_id = await self._get_genre_id(genre)
        if not genre_id:
            return f"Error: Genre '{genre}' not recognized. Please use one of the available genres."

        url = f"https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": self._tmdb_api_key,
            "with_genres": genre_id,
            "sort_by": "popularity.desc",
            "language": "en-US",
            "page": 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if response.status != 200:
                    return f"Error from TMDB API: {data.get('status_message', 'Unknown error')}"

                results = data.get("results", [])[:5]
                if not results:
                    return f"No movies found for genre '{genre}'."

                output = f"Top movie recommendations in '{genre.title()}' genre:\n"
                for idx, movie in enumerate(results, 1):
                    title = movie.get("title", "N/A")
                    year = movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A"
                    output += f"{idx}. {title} ({year})\n"
                return output.strip()

    async def _get_movie_details(self, title: str) -> str:
        """Fetch detailed information about a movie using both TMDB and OMDb APIs."""
        tmdb_id = await self._get_tmdb_id_by_title(title)
        if not tmdb_id:
            return f"Could not find movie with title '{title}'."

        tmdb_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {"api_key": self._tmdb_api_key, "language": "en-US"}
        async with aiohttp.ClientSession() as session:
            async with session.get(tmdb_url, params=params) as tmdb_response:
                tmdb_data = await tmdb_response.json()
                if tmdb_response.status != 200:
                    return f"Error fetching TMDB details: {tmdb_data.get('status_message', 'Unknown error')}"

                omdb_data = {}
                if self._omdb_api_key:
                    omdb_url = "http://www.omdbapi.com/"
                    omdb_params = {"apikey": self._omdb_api_key, "t": title}
                    async with session.get(omdb_url, params=omdb_params) as omdb_response:
                        if omdb_response.status == 200:
                            omdb_data = await omdb_response.json()

                output = f"Movie: {tmdb_data.get('title', 'N/A')}\n"
                output += f"Release Date: {tmdb_data.get('release_date', 'N/A')}\n"
                output += f"Genres: {', '.join([genre['name'] for genre in tmdb_data.get('genres', [])])}\n"
                output += f"Overview: {tmdb_data.get('overview', 'N/A')}\n"
                output += f"Rating: {tmdb_data.get('vote_average', 'N/A')} ({tmdb_data.get('vote_count', 0)} votes)\n"

                if omdb_data and omdb_data.get('Response') == 'True':
                    output += f"IMDb Rating: {omdb_data.get('imdbRating', 'N/A')}\n"
                    output += f"Director: {omdb_data.get('Director', 'N/A')}\n"
                    output += f"Actors: {omdb_data.get('Actors', 'N/A')}\n"
                    output += f"Awards: {omdb_data.get('Awards', 'N/A')}\n"

                return output.strip()

    async def _get_genre_id(self, genre_name: str) -> Optional[int]:
        genre_map = {
            "action": 28, "adventure": 12, "animation": 16, "comedy": 35,
            "crime": 80, "documentary": 99, "drama": 18, "family": 10751,
            "fantasy": 14, "history": 36, "horror": 27, "music": 10402,
            "mystery": 9648, "romance": 10749, "science_fiction": 878,
            "thriller": 53, "tv_movie": 10770, "war": 10752, "western": 37
        }
        return genre_map.get(genre_name.lower())

    async def _get_tmdb_id_by_title(self, title: str) -> Optional[int]:
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {"api_key": self._tmdb_api_key, "query": title, "language": "en-US"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                if response.status == 200 and data.get("results"):
                    return data["results"][0].get("id")
                return None
