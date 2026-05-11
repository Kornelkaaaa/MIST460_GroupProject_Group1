import streamlit as st

from fetch_data import fetch_data, fetch_raw, require_login


def manage_reviews_ui():
    st.header("Edit or Delete a Review")

    gamer_id = require_login()
    if gamer_id is None:
        return

    library_df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})
    if library_df is None or library_df.empty:
        st.info("Your library is empty.")
        return

    st.caption("Pick a game from your library:")
    game_title = st.selectbox("Game", list(library_df["GameTitle"]))

    st.divider()
    st.subheader("Edit existing review")

    new_rating = st.slider(
        "New rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1, key="edit_rating"
    )
    new_text = st.text_area("New review text (optional)", key="edit_text")

    if st.button("Update review"):
        params = {
            "gamer_id": gamer_id,
            "game_title": game_title,
            "rating": float(new_rating),
        }
        if new_text.strip():
            params["review_text"] = new_text.strip()

        payload = fetch_raw("update_review/", params)
        if not payload:
            return
        if "error" in payload:
            st.error(f"Update failed: {payload['error']}")
            return
        st.success("Review updated.")
        data = payload.get("data") or {}
        if data:
            st.write(data)

    st.divider()
    st.subheader("Delete review")

    confirm = st.checkbox("Yes, delete my review for this game.", key="del_confirm")
    if st.button("Delete review", disabled=not confirm):
        payload = fetch_raw(
            "delete_review/",
            {"gamer_id": gamer_id, "game_title": game_title},
        )
        if not payload:
            return
        if "error" in payload:
            st.error(f"Delete failed: {payload['error']}")
            return
        rows_deleted = (payload.get("data") or {}).get("RowsDeleted", 0)
        if rows_deleted:
            st.success(f"Review deleted ({rows_deleted} row).")
        else:
            st.info("No review existed for this game — nothing to delete.")
