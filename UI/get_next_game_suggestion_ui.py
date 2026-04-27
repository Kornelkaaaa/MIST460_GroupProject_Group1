import streamlit as st

from fetch_data import fetch_data


def get_next_game_suggestion_ui():
    st.header("What Should I Play Next?")

    default_id = st.session_state.get("app_user_id", "")
    gamer_id = st.text_input("Gamer ID", value=str(default_id) if default_id else "")

    if st.button("Get Suggestion"):
        if not gamer_id.strip().isdigit():
            st.error("Gamer ID must be a number.")
            return

        df = fetch_data("get_next_game_suggestion/", {"gamer_id": int(gamer_id)})

        if df is not None and not df.empty:
            row = df.iloc[0]
            reason = row.get("SuggestionReason")
            if reason:
                st.success(reason)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No suggestion available — try adding more games to your library.")
