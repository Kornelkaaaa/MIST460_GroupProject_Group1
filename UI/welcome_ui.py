import streamlit as st

from fetch_data import current_user_id, current_user_name, current_user_role


def welcome_ui():
    st.header("🎮 Welcome to the MIST 460 Game Recommender")

    name = current_user_name()
    role = current_user_role()
    uid = current_user_id()

    if uid is not None:
        st.success(f"Signed in as **{name}** ({role}) — AppUserID `{uid}`.")
    else:
        st.info(
            "You're browsing as a guest. **Log in** to get personalized "
            "recommendations and access your library."
        )

    st.divider()
    st.subheader("What you can do here")

    if role == "Developer":
        st.markdown(
            "- 📊 **Developer Analytics** — review the performance of each "
            "game in your studio's catalog: ownership, completion rates, "
            "sentiment buckets, and player segments."
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                "**Discover games**\n"
                "- 🤖 AI recommendations driven by review embeddings\n"
                "- 🔍 Keyword search across the catalog"
            )
        with col2:
            st.markdown(
                "**Manage your library**\n"
                "- 📚 View every game you own + your play stats\n"
                "- ➕ Add games from the catalog\n"
                "- 🎯 Update status (In Progress, Completed, …) and hours\n"
                "- ⭐ Write and edit reviews"
            )

    st.divider()
    st.subheader("Try this first")

    if uid is None:
        st.markdown(
            "1. Use the sidebar to open **🔑 Log in / Sign up**\n"
            "2. Sign in with one of the test accounts (e.g. `alex.rivera@email.com` / `alex123`) or create a new one\n"
            "3. Browse to **🤖 AI Recommendations** and ask for something like "
            "*\"colorful, cheerful platformer I can play with my kids\"*"
        )
    elif role == "Developer":
        st.markdown(
            "Open **📊 Developer Analytics** in the sidebar and select one of your games."
        )
    else:
        st.markdown(
            "Open **🤖 AI Recommendations** in the sidebar and try one of the suggestion chips — or describe in your own words what you're in the mood to play."
        )
