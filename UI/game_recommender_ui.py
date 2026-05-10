import streamlit as st

from validate_user_ui import validate_user_ui
from full_gamer_onboarding_ui import full_gamer_onboarding_ui
from get_recommendations_ui import get_recommendations_ui
from search_games_ui import search_games_ui
from get_next_game_suggestion_ui import get_next_game_suggestion_ui
from add_game_to_library_ui import add_game_to_library_ui
from update_game_status_ui import update_game_status_ui
from submit_review_ui import submit_review_ui
from get_developer_analytics_ui import get_developer_analytics_ui
from get_gamer_library_ui import get_gamer_library_ui


st.set_page_config(page_title="Game Recommender", layout="wide")
st.title("MIST 460 — Game Recommender (Group 1)")

if "app_user_id" not in st.session_state:
    st.session_state.app_user_id = None
if "app_user_name" not in st.session_state:
    st.session_state.app_user_name = None


# ─────────── Sidebar: login status + logout ───────────

with st.sidebar:
    st.subheader("Account")
    if st.session_state.app_user_id:
        st.write(
            f"Logged in as **{st.session_state.app_user_name or '?'}**  \n"
            f"AppUserID: `{st.session_state.app_user_id}`"
        )
        if st.button("Log out"):
            st.session_state.app_user_id = None
            st.session_state.app_user_name = None
            st.rerun()
    else:
        st.info("Not logged in")

    st.divider()


# ─────────── Sidebar: page selector ───────────

GAMER_PAGES = {
    "Validate User Credentials": validate_user_ui,
    "Sign Up": full_gamer_onboarding_ui,
    "My Library & Stats": get_gamer_library_ui,
    "Get Game Recommendations": get_recommendations_ui,
    "Search Games by Keyword": search_games_ui,
    "What Should I Play Next?": get_next_game_suggestion_ui,
    "Add Game to Library": add_game_to_library_ui,
    "Update Game Status": update_game_status_ui,
    "Submit a Review": submit_review_ui,
}

DEVELOPER_PAGES = {
    "Validate User Credentials": validate_user_ui,
    "Developer Analytics": get_developer_analytics_ui,
}

role = st.session_state.get("app_user_role")
if role == "Developer":
    pages = DEVELOPER_PAGES
else:
    # Gamers and not-logged-in users see the gamer menu.
    pages = GAMER_PAGES

choice = st.sidebar.selectbox("Choose a feature", list(pages.keys()))
pages[choice]()
