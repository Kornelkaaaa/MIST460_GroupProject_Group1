import streamlit as st

from validate_user_ui import validate_user_ui
from get_recommendations_ui import get_recommendations_ui
from search_games_ui import search_games_ui
from get_next_game_suggestion_ui import get_next_game_suggestion_ui
from get_developer_analytics_ui import get_developer_analytics_ui


st.set_page_config(page_title="Game Recommender", layout="wide")
st.title("MIST 460 — Game Recommender (Group 1)")

if "app_user_id" not in st.session_state:
    st.session_state.app_user_id = None

menu = st.sidebar.selectbox(
    "Choose a feature",
    (
        "Validate User Credentials",
        "Get Game Recommendations",
        "Search Games by Keyword",
        "What Should I Play Next?",
        "Developer Analytics",
    ),
)

if menu == "Validate User Credentials":
    validate_user_ui()
elif menu == "Get Game Recommendations":
    get_recommendations_ui()
elif menu == "Search Games by Keyword":
    search_games_ui()
elif menu == "What Should I Play Next?":
    get_next_game_suggestion_ui()
elif menu == "Developer Analytics":
    get_developer_analytics_ui()
