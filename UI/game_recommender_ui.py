import streamlit as st

from welcome_ui import welcome_ui
from validate_user_ui import validate_user_ui
from full_gamer_onboarding_ui import full_gamer_onboarding_ui
from search_games_ui import search_games_ui
from add_game_to_library_ui import add_game_to_library_ui
from update_game_status_ui import update_game_status_ui
from submit_review_ui import submit_review_ui
from get_developer_analytics_ui import get_developer_analytics_ui
from get_gamer_library_ui import get_gamer_library_ui
from remove_game_from_library_ui import remove_game_from_library_ui
from manage_reviews_ui import manage_reviews_ui
from update_gamer_profile_ui import update_gamer_profile_ui
from embedding_recommendations_ui import embedding_recommendations_ui


st.set_page_config(page_title="Game Recommender", layout="wide", page_icon="🎮")

# ──────────────── Session bootstrap ────────────────

for key in ("app_user_id", "app_user_name", "app_user_role"):
    if key not in st.session_state:
        st.session_state[key] = None


# ──────────────── Page registry ────────────────
# Pages are organised into sections for visual grouping in the sidebar.
# Each entry is "Section · Page" so users can scan the dropdown
# quickly. The list-of-tuples format keeps insertion order.

GAMER_PAGES = [
    ("🏠 Home",      "Welcome",                    welcome_ui),
    ("🔑 Account",   "Log in / Validate",          validate_user_ui),
    ("🔑 Account",   "Sign up",                    full_gamer_onboarding_ui),
    ("🔑 Account",   "Edit my profile",            update_gamer_profile_ui),
    ("📚 Library",   "My library & stats",         get_gamer_library_ui),
    ("📚 Library",   "Add a game",                 add_game_to_library_ui),
    ("📚 Library",   "Remove a game",              remove_game_from_library_ui),
    ("📚 Library",   "Update game status",         update_game_status_ui),
    ("✨ Discover",  "🤖 AI recommendations",      embedding_recommendations_ui),
    ("✨ Discover",  "Search by keyword",          search_games_ui),
    ("⭐ Reviews",   "Submit a review",            submit_review_ui),
    ("⭐ Reviews",   "Edit or delete a review",    manage_reviews_ui),
]

DEVELOPER_PAGES = [
    ("🏠 Home",      "Welcome",                    welcome_ui),
    ("🔑 Account",   "Log in / Validate",          validate_user_ui),
    ("📊 Studio",    "Developer analytics",        get_developer_analytics_ui),
]


role = st.session_state.app_user_role
PAGES = DEVELOPER_PAGES if role == "Developer" else GAMER_PAGES

label_to_handler = {f"{section}  ·  {name}": fn for section, name, fn in PAGES}


# ──────────────── Sidebar ────────────────

with st.sidebar:
    st.markdown("## 🎮 Game Recommender")

    if st.session_state.app_user_id:
        st.markdown(
            f"**{st.session_state.app_user_name or '?'}**  \n"
            f"`{st.session_state.app_user_role or 'Gamer'}`  ·  ID `{st.session_state.app_user_id}`"
        )
        if st.button("Log out", use_container_width=True):
            st.session_state.app_user_id = None
            st.session_state.app_user_name = None
            st.session_state.app_user_role = None
            st.rerun()
    else:
        st.info("Not logged in")

    st.divider()

    choice = st.selectbox(
        "Navigate",
        list(label_to_handler.keys()),
    )


# ──────────────── Top banner + page render ────────────────

# Friendly heads-up when a guest lands on a feature that needs login.
if (
    not st.session_state.app_user_id
    and choice not in ("🏠 Home  ·  Welcome", "🔑 Account  ·  Log in / Validate", "🔑 Account  ·  Sign up")
):
    st.warning(
        "You're not signed in. Open **🔑 Account → Log in / Validate** "
        "in the sidebar to access personalized features."
    )

label_to_handler[choice]()
