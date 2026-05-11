import streamlit as st

from fetch_data import fetch_raw, require_login


DIFFICULTY_OPTIONS = ["", "Easy", "Medium", "Hard", "Expert"]
PLAY_STYLE_OPTIONS = ["", "Completionist", "Casual", "Speedrunner", "Story-Driven"]
MODE_OPTIONS = ["", "Single-Player", "Multiplayer", "Co-op"]


def _index_or_zero(options, value):
    return options.index(value) if value in options else 0


def update_gamer_profile_ui():
    st.header("Edit My Profile")

    gamer_id = require_login()
    if gamer_id is None:
        return

    payload = fetch_raw("get_gamer_profile/", {"gamer_id": gamer_id})
    if not payload or not payload.get("data"):
        st.error("Could not load your profile.")
        return

    current = payload["data"]
    st.caption(f"Email: {current.get('Email', '?')}  (email cannot be changed here)")

    col1, col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First name", value=current.get("FirstName") or "")
        phone = st.text_input("Phone", value=current.get("Phone") or "")
        preferred_genres = st.text_input(
            "Preferred genres (comma-separated)",
            value=current.get("PreferredGenres") or "",
        )
    with col2:
        last_name = st.text_input("Last name", value=current.get("LastName") or "")
        available_play_time = st.number_input(
            "Available play time (hours/week)",
            min_value=0.0,
            max_value=168.0,
            value=float(current.get("AvailablePlayTime") or 0.0),
        )

    preferred_difficulty = st.selectbox(
        "Preferred difficulty",
        DIFFICULTY_OPTIONS,
        index=_index_or_zero(DIFFICULTY_OPTIONS, current.get("PreferredDifficulty") or ""),
    )
    preferred_play_style = st.selectbox(
        "Preferred play style",
        PLAY_STYLE_OPTIONS,
        index=_index_or_zero(PLAY_STYLE_OPTIONS, current.get("PreferredPlayStyle") or ""),
    )
    preferred_mode = st.selectbox(
        "Preferred mode",
        MODE_OPTIONS,
        index=_index_or_zero(MODE_OPTIONS, current.get("PreferredMode") or ""),
    )

    if st.button("Save changes"):
        params = {"gamer_id": gamer_id}
        if first_name.strip():
            params["first_name"] = first_name.strip()
        if last_name.strip():
            params["last_name"] = last_name.strip()
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

        result = fetch_raw("update_gamer_profile/", params)
        if not result:
            return
        if "error" in result:
            st.error(f"Update failed: {result['error']}")
            return

        # Refresh the cached display name so the sidebar shows the new value.
        new_full = f"{first_name.strip()} {last_name.strip()}".strip()
        if new_full:
            st.session_state.app_user_name = new_full

        st.success("Profile updated.")
        st.write(result.get("data") or {})
