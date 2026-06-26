import os
from typing import List
from langchain_openai import ChatOpenAI
from app.schemas import Diner
from app.filter import filter_restaurants
from app.yelp import fetch_live_restaurants

def get_recommendations(query: str, diners: List[Diner], user_lat: float, user_lon: float, max_distance_miles: float) -> str:
    """
    Filters restaurants based on active diner vetoes and distance, then uses LangChain + OpenAI
    to generate a conversational suggestion.
    """

    live_restaurants = fetch_live_restaurants(user_lat, user_lon, max_distance_miles)

    # 1. Filter restaurants using our core logic
    allowed_restaurants = filter_restaurants(
        restaurants=live_restaurants,
        diners=diners,
        user_lat=user_lat,
        user_lon=user_lon,
        max_distance_miles=max_distance_miles
    )

    # 2. Format context for the LLM
    restaurants_context = "\n".join([f"= {r.name} (Cuisine: {r.cuisine}, Rating: {r.rating}, Price: {'$' * r.price_level}, Address: {r.address})"
                                     for r in allowed_restaurants
                                     ])
    
    active_diners = [d for d in diners if d.is_active]
    diners_context = "\n".join([f"- {d.name} (Dislikes: {', '.join(d.dislikes)})"
                                for d in active_diners
                                ])
    
    prompt = f"""You are WeEat, a friendly family meal planner AI assistant. 
Your goal is to suggest where to eat based on the user's request and the diners eating.
ACTIVE DINERS & THEIR DISLIKES:
{diners_context if active_diners else "No active diner preferences (anyone eats anything)."}
AVAILABLE RESTAURANTS (Filtered to fit distance and veto criteria):
{restaurants_context if allowed_restaurants else "No matching restaurants found."}
USER REQUEST: {query}
INSTRUCTIONS:
1. Recommend one or more restaurants from the available list that fit the user's request.
2. Politely explain why they fit and highlight that you have respected the active diners' dislikes.
3. If no restaurants are available, explain why (e.g., all local options are vetoed) and suggest checking diner settings.
4. Keep the response friendly, helpful, and concise. Do not suggest any restaurants not in the available list.
"""
    
    # 3. LLM Invocation or Mock Fallback
    api_key = os.getenv("OPENAI_API_KEY", "")

    # Check if we should Mock LLM mode (if key is empty or placeholder)
    if not api_key or api_key == "your-openai-api-key" or api_key.startswith("["):
        # Mock response simulation
        if not allowed_restaurants:
            return "I couldn't find any restaurants within the range that satisfies everyone's dislikes. Try adjusting the toggles or searching a bit futher!"
        
        rec_names = ", ".join([r.name for r in allowed_restaurants[:2]])
        return f"[Mock AI Response] Based on your preferences, I recommend: {rec_names}. They respect all active diner vetoes!"
    
    # Real LLM call using LangChain
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=api_key, temperature=0.7)
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        return f"[Agent Error: {str(e)}] Falling back to mock suggestions: " + ", ".join([r.name for r in allowed_restaurants[:2]])