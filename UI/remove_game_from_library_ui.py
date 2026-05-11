import streamlit as st

from fetch_data import fetch_data, fetch_raw, require_login


def remove_game_from_library_ui():
    st.header("Remove Game from Your Library")

    gamer_id = require_login()
    if gamer_id is None:
        return

    library_df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})
    if library_df is None or library_df.empty:
        st.info("Your library is empty — nothing to remove.")
        return

    st.caption("Type to filter the list:")
    game_title = st.selectbox("Game", list(library_df["GameTitle"]))

    st.warning(
        "Removing a game deletes your play stats for it (hours, status). "
        "Your review (if any) is **not** deleted."
    )

    confirm = st.checkbox("Yes, I'm sure I want to remove this game.")

    if st.button("Remove from Library", disabled=not confirm):
        payload = fetch_raw(
            "remove_game_from_library/",
            {"gamer_id": gamer_id, "game_title": game_title},
        )
        if not payload:
            return
        if "error" in payload:
            st.error(f"Could not remove: {payload['error']}")
            return
        st.success(f"Removed **{game_title}** from your library.")
