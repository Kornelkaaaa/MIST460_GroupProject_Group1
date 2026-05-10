import streamlit as st

from fetch_data import fetch_data, require_login


def get_recommendations_ui():
    st.header("Get Game Recommendations")

    gamer_id = require_login()
    if gamer_id is None:
        return

    top_n = st.number_input(
        "How many recommendations?", min_value=1, max_value=50, value=6
    )

    if st.button("Fetch Recommendations"):
        df = fetch_data(
            "get_recommendations/",
            {"gamer_id": gamer_id, "top_n": int(top_n)},
        )

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recommendations available for this gamer.")
