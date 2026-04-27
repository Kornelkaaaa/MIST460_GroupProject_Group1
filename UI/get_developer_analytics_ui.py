import pandas as pd
import streamlit as st

from fetch_data import fetch_raw


def get_developer_analytics_ui():
    st.header("Developer Analytics Dashboard")

    game_title = st.text_input("Game Title (exact name from your catalog)")
    developer_id = st.text_input("Your Developer ID")

    if st.button("Load Analytics"):
        if not game_title.strip():
            st.error("Game Title is required.")
            return
        if not developer_id.strip().isdigit():
            st.error("Developer ID must be a number.")
            return

        payload = fetch_raw(
            "get_developer_analytics/",
            {"game_title": game_title.strip(), "developer_id": int(developer_id)},
        )

        if not payload:
            return

        summary = pd.DataFrame(payload.get("summary", []))
        sentiment = pd.DataFrame(payload.get("sentiment", []))
        player_profile = pd.DataFrame(payload.get("player_profile", []))

        st.subheader("Performance Summary")
        if summary.empty:
            st.info("No summary data available — check the title and that this game belongs to you.")
        else:
            st.dataframe(summary, use_container_width=True, hide_index=True)

        st.subheader("Review Sentiment")
        if sentiment.empty:
            st.info("No reviews yet.")
        else:
            st.dataframe(sentiment, use_container_width=True, hide_index=True)

        st.subheader("Player Profile Breakdown")
        if player_profile.empty:
            st.info("No player profile data yet.")
        else:
            st.dataframe(player_profile, use_container_width=True, hide_index=True)
