import streamlit as st

from fetch_data import fetch_data


def get_recommendations_ui():
    st.header("Get Game Recommendations")

    default_id = st.session_state.get("app_user_id", "")
    gamer_id = st.text_input("Gamer ID", value=str(default_id) if default_id else "")
    top_n = st.number_input("How many recommendations?", min_value=1, max_value=50, value=6)

    if st.button("Fetch Recommendations"):
        if not gamer_id.strip().isdigit():
            st.error("Gamer ID must be a number.")
            return

        df = fetch_data(
            "get_recommendations/",
            {"gamer_id": int(gamer_id), "top_n": int(top_n)},
        )

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No recommendations available for this gamer.")
