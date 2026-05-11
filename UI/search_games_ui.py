import streamlit as st

from fetch_data import current_user_id, fetch_data


def search_games_ui():
    st.header("🔍 Search Games by Keyword")
    st.caption("Searches title, description, studio name, and genre.")

    keyword = st.text_input("Keyword", placeholder="open world, FPS, …")
    top_n = st.slider("Maximum results", min_value=1, max_value=50, value=10)

    logged_in = current_user_id()
    if logged_in is not None:
        st.caption(f"Owned games for Gamer {logged_in} will be flagged in the results.")

    if st.button("Search", type="primary"):
        if not keyword.strip():
            st.error("Please type a keyword.")
            return

        params = {"keyword": keyword.strip(), "top_n": int(top_n)}
        if logged_in is not None:
            params["gamer_id"] = logged_in

        df = fetch_data(
            "search_games_by_keyword/",
            params,
            spinner_text=f"Searching for '{keyword.strip()}'…",
        )
        if df is None:
            return
        if df.empty:
            st.info("No games matched your keyword. Try a broader term.")
            return

        st.success(f"{len(df)} match{'es' if len(df) != 1 else ''}.")

        for _, row in df.iterrows():
            owned = row.get("AlreadyOwned") == "Yes"
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    title_badge = " ✓ in your library" if owned else ""
                    st.markdown(
                        f"### {row.get('GameTitle', '?')}{title_badge}  \n"
                        f"*{row.get('StudioName', '?')} · {row.get('YearReleased', '?')} · "
                        f"{row.get('PrimaryGenre', '?')}*"
                    )
                    desc = row.get("GameDescription")
                    if desc:
                        st.markdown(desc)
                    completion = row.get("CompletionRatePct")
                    if completion is not None:
                        st.caption(f"Community completion rate: {float(completion):.1f}%")
                with cols[1]:
                    rating = row.get("AverageRating")
                    if rating is not None:
                        st.metric("Avg rating", f"{float(rating):.2f}/5")
