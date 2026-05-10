import streamlit as st

from fetch_data import fetch_data, fetch_raw, require_login


def add_game_to_library_ui():
    st.header("Add Game to Your Library")

    gamer_id = require_login()
    if gamer_id is None:
        return

    catalog_df = fetch_data("get_all_games/", {})
    if catalog_df is None or catalog_df.empty:
        st.warning("Catalog is empty.")
        return

    library_df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})
    owned_titles = (
        set(library_df["GameTitle"]) if library_df is not None and not library_df.empty else set()
    )

    available = catalog_df[~catalog_df["GameTitle"].isin(owned_titles)].copy()
    if available.empty:
        st.success("You already own every game in the catalog! 🎮")
        return

    available["label"] = (
        available["GameTitle"]
        + "  —  "
        + available["StudioName"].fillna("")
        + "  ("
        + available["YearReleased"].astype("Int64").astype(str)
        + ")"
    )

    st.caption("Type to filter the list:")
    label = st.selectbox("Game", available["label"].tolist())

    chosen_title = available.loc[available["label"] == label, "GameTitle"].iloc[0]

    if st.button("Add to Library"):
        payload = fetch_raw(
            "add_game_to_library/",
            {"gamer_id": gamer_id, "game_title": chosen_title},
        )
        if not payload:
            return

        if "error" in payload:
            st.error(f"Could not add: {payload['error']}")
            return

        new_lib_id = payload.get("data", {}).get("NewLibraryID")
        if new_lib_id is not None:
            st.success(f"Added **{chosen_title}**! New LibraryID: {new_lib_id}")
        else:
            st.success(f"Added **{chosen_title}** to your library.")
