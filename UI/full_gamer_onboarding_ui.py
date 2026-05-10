import pandas as pd
import streamlit as st

from fetch_data import fetch_raw


DIFFICULTY_OPTIONS = ["", "Easy", "Medium", "Hard", "Expert"]
PLAY_STYLE_OPTIONS = ["", "Completionist", "Casual", "Speedrunner", "Story-Driven"]
MODE_OPTIONS = ["", "Single-Player", "Multiplayer", "Co-op"]


def full_gamer_onboarding_ui():
    st.header("Full Gamer Onboarding")
    st.caption(
        "Registers a new gamer, adds any games they already own, and returns their first recommendations."
    )

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name *")
        email = st.text_input("Email *")
        phone = st.text_input("Phone (optional)")
        preferred_genres = st.text_input(
            "Preferred Genres (e.g. 'Action, RPG')"
        )
    with col2:
        last_name = st.text_input("Last Name *")
        password = st.text_input("Password *", type="password")
        available_play_time = st.number_input(
            "Available play time (hours/week)", min_value=0.0, max_value=168.0, value=0.0
        )

    preferred_difficulty = st.selectbox("Preferred Difficulty", DIFFICULTY_OPTIONS)
    preferred_play_style = st.selectbox("Preferred Play Style", PLAY_STYLE_OPTIONS)
    preferred_mode = st.selectbox("Preferred Mode", MODE_OPTIONS)
    owned_game_titles = st.text_input(
        "Games you already own (pipe-separated, e.g. 'Diablo IV|Far Cry 6')"
    )

    if st.button("Onboard Me"):
        if not (first_name.strip() and last_name.strip() and email.strip() and password.strip()):
            st.error("First name, last name, email, and password are required.")
            return

        params = {
            "first_name": first_name.strip(),
            "last_name": last_name.strip(),
            "email": email.strip(),
            "password": password,
        }
        if phone.strip():
            params["phone"] = phone.strip()
        if preferred_genres.strip():
            params["preferred_genres"] = preferred_genres.strip()
        if preferred_difficulty:
            params["preferred_difficulty"] = preferred_difficulty
        if preferred_play_style:
            params["preferred_play_style"] = preferred_play_style
        if preferred_mode:
            params["preferred_mode"] = preferred_mode
        if available_play_time > 0:
            params["available_play_time"] = float(available_play_time)
        if owned_game_titles.strip():
            params["owned_game_titles"] = owned_game_titles.strip()

        payload = fetch_raw("full_gamer_onboarding/", params)
        if not payload:
            return

        if "error" in payload:
            st.error(f"Onboarding failed: {payload['error']}")
            return

        data = payload.get("data") or {}
        confirmation = data.get("confirmation") or {}
        recommendations = data.get("recommendations") or []

        new_id = confirmation.get("NewGamerID")
        message = confirmation.get("Message", "Onboarding complete.")
        if new_id:
            st.success(f"{message} Your Gamer ID is {new_id}.")
        else:
            st.success(message)

        if recommendations:
            st.subheader("Your first recommendations")
            st.dataframe(pd.DataFrame(recommendations), use_container_width=True, hide_index=True)
