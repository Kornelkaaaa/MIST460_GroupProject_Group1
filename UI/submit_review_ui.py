import streamlit as st

from fetch_data import fetch_data, fetch_raw, require_login


def submit_review_ui():
    st.header("Submit a Game Review")

    gamer_id = require_login()
    if gamer_id is None:
        return

    library_df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})
    if library_df is None or library_df.empty:
        st.info("Your library is empty. Add a game first.")
        return

    titles = list(library_df["GameTitle"])
    game_title = st.selectbox("Game (from your library)", titles)
    rating = st.slider("Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
    review_text = st.text_area("Review (optional)")

    if st.button("Submit Review"):
        params = {
            "gamer_id": gamer_id,
            "game_title": game_title,
            "rating": float(rating),
        }
        if review_text.strip():
            params["review_text"] = review_text.strip()

        payload = fetch_raw("submit_review/", params)
        if not payload:
            return

        if "error" in payload:
            st.error(f"Review failed: {payload['error']}")
            return

        data = payload.get("data") or {}
        st.success("Review submitted.")
        if data:
            st.write(data)
