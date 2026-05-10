import streamlit as st

from fetch_data import fetch_data, require_login


def get_next_game_suggestion_ui():
    st.header("What Should I Play Next?")

    gamer_id = require_login()
    if gamer_id is None:
        return

    if st.button("Get Suggestion"):
        df = fetch_data("get_next_game_suggestion/", {"gamer_id": gamer_id})

        if df is not None and not df.empty:
            row = df.iloc[0]
            reason = row.get("SuggestionReason")
            if reason:
                st.success(reason)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No suggestion available — try adding more games to your library.")
