import pandas as pd
import streamlit as st

from fetch_data import current_user_id, current_user_role, fetch_data, fetch_raw


def get_developer_analytics_ui():
    st.header("Developer Analytics Dashboard")

    logged_in = current_user_id()
    role = current_user_role()

    if logged_in is None:
        st.warning("Please log in first using **Validate User Credentials**.")
        return

    if role != "Developer":
        st.error(
            "This page is only available to Developer accounts. "
            f"You are signed in as a **{role or 'Gamer'}**."
        )
        return

    st.caption(f"Using your Developer ID: {logged_in}")
    developer_id = logged_in

    games_df = fetch_data("get_developer_games/", {"developer_id": developer_id})
    if games_df is None:
        return
    if games_df.empty:
        st.info("You don't have any games in the catalog yet.")
        return

    games_df = games_df.copy()
    games_df["label"] = (
        games_df["GameTitle"]
        + "  ("
        + games_df["YearReleased"].astype("Int64").astype(str)
        + ")"
    )

    st.caption("Type to filter your games:")
    label = st.selectbox("Game", games_df["label"].tolist())
    game_title = games_df.loc[games_df["label"] == label, "GameTitle"].iloc[0]

    if st.button("Load Analytics"):
        payload = fetch_raw(
            "get_developer_analytics/",
            {"game_title": game_title, "developer_id": developer_id},
        )

        if not payload:
            return

        summary = pd.DataFrame(payload.get("summary", []))
        sentiment = pd.DataFrame(payload.get("sentiment", []))
        player_profile = pd.DataFrame(payload.get("player_profile", []))

        st.subheader("Performance Summary")
        if summary.empty:
            st.info("No summary data — check the title and that this game belongs to you.")
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
