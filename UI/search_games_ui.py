import streamlit as st

from fetch_data import current_user_id, fetch_data


def search_games_ui():
    st.header("Search Games by Keyword")

    keyword = st.text_input("Keyword (title, description, studio, or genre)")
    top_n = st.number_input("Maximum results", min_value=1, max_value=100, value=10)

    logged_in = current_user_id()
    if logged_in is not None:
        st.caption(f"Will flag games already in Gamer {logged_in}'s library.")

    if st.button("Search"):
        if not keyword.strip():
            st.error("Keyword is required.")
            return

        params = {"keyword": keyword.strip(), "top_n": int(top_n)}
        if logged_in is not None:
            params["gamer_id"] = logged_in

        df = fetch_data("search_games_by_keyword/", params)

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No games matched your keyword.")
