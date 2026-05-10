import streamlit as st

from fetch_data import fetch_data, fetch_raw, require_login


STATUS_OPTIONS = ["Not Started", "In Progress", "Completed", "Abandoned"]


def update_game_status_ui():
    st.header("Update Game Status")

    gamer_id = require_login()
    if gamer_id is None:
        return

    library_df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})
    if library_df is None or library_df.empty:
        st.info("Your library is empty. Add a game first.")
        return

    title_to_status = dict(zip(library_df["GameTitle"], library_df["Status"]))
    titles = list(library_df["GameTitle"])

    game_title = st.selectbox("Game (from your library)", titles)
    current_status = title_to_status.get(game_title, "Not Started")
    st.caption(f"Current status: **{current_status}**")

    default_idx = STATUS_OPTIONS.index(current_status) if current_status in STATUS_OPTIONS else 1
    new_status = st.selectbox("New Status", STATUS_OPTIONS, index=default_idx)
    hours_played_str = st.text_input(
        "Hours Played (optional — leave blank to keep current)"
    )

    if st.button("Update"):
        params = {
            "gamer_id": gamer_id,
            "game_title": game_title,
            "new_status": new_status,
        }
        if hours_played_str.strip():
            try:
                params["hours_played"] = float(hours_played_str)
            except ValueError:
                st.error("Hours played must be a number.")
                return

        payload = fetch_raw("update_game_status/", params)
        if not payload:
            return

        if "error" in payload:
            st.error(f"Update failed: {payload['error']}")
            return

        data = payload.get("data") or {}
        st.success("Status updated.")
        if data:
            st.write(data)
