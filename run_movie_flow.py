# run_movie_flow.py
import asyncio
from app.agent.manus import Manus
from app.flow.movie_recommendation_flow import MovieRecommendationFlow

async def main():
    manus_agent = Manus()
    agents = {"manus": manus_agent}
    flow = MovieRecommendationFlow(agents=agents)

    result = await flow.execute("I want to watch a good comedy movie. Can you recommend some?")
    print("\n=== Movie Recommendation ===\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
