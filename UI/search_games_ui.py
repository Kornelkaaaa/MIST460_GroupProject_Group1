import streamlit as st

from fetch_data import fetch_data


def search_games_ui():
    st.header("Search Games by Keyword")

    keyword = st.text_input("Keyword (title, description, studio, or genre)")
    default_id = st.session_state.get("app_user_id", "")
    gamer_id = st.text_input(
        "Gamer ID (optional — flags games you already own)",
        value=str(default_id) if default_id else "",
    )
    top_n = st.number_input("Maximum results", min_value=1, max_value=100, value=10)

    if st.button("Search"):
        if not keyword.strip():
            st.error("Keyword is required.")
            return

        params = {"keyword": keyword.strip(), "top_n": int(top_n)}
        if gamer_id.strip().isdigit():
            params["gamer_id"] = int(gamer_id)

        df = fetch_data("search_games_by_keyword/", params)

        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No games matched your keyword.")
