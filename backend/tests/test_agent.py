import pytest
from unittest.mock import patch, MagicMock
from app.schemas import Diner
from app.agent import get_recommendations
from tests.test_filtering import MOCK_RESTAURANTS

def test_agent_includes_restaurant_context():
    """
    Verify that the agent prompt filters the restaurants using diner vetoes, includes active diner preferences,
    and invokes the LLM with the correct context.
    """
    # Olivia dislikes pizza so Streamwood Pizza Co should be filtered out
    diners = [Diner(name="Olivia", is_active=True, dislikes=["pizza"])]
    query = "Recommend a place to eat near me"

    with patch("app.agent.ChatOpenAI") as mock_chat_openai, \
         patch("app.agent.fetch_live_restaurants", return_value=MOCK_RESTAURANTS), \
         patch("app.agent.os.getenv", return_value="sk-test-key"):
        mock_instance = MagicMock()
        mock_instance.invoke.return_value.content = "I recommend Elgin Burger Joint because you dislike pizza."
        mock_chat_openai.return_value = mock_instance

        response = get_recommendations(
            query=query,
            diners=diners,
            user_lat=42.0234,
            user_lon=-88.1837,
            max_distance_miles=15.0
        )

        # Verify response matches LLM output
        assert "Elgin Burger Joint" in response

        # Verify ChatOpenAI was instantiated
        mock_chat_openai.assert_called_once()

        # Extract the prompt sent to the LLM
        args, kwargs = mock_instance.invoke.call_args
        prompt_text = args[0]

        # The prompt should contain the diner details
        assert "Olivia" in prompt_text
        assert "pizza" in prompt_text

        # The prompt should contain the allowed restaurant list
        assert "Elgin Burger Joint" in prompt_text

        # The prompt should NOT contain Streamwood Pizza Co because Olivis dislikes pizza
        assert "Streamwood Pizza Co" not in prompt_text