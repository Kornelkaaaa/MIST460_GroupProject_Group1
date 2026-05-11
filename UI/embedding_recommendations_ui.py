import streamlit as st

from fetch_data import current_user_id, fetch_raw


SUGGESTIONS = [
    "colorful, cheerful platformer I can play with my kids on the couch",
    "dark gothic world with loot grinding and hundreds of hours of endgame",
    "open-world first-person shooter with a charismatic villain",
    "stealth action in a historical setting, not too long",
    "3D platformer with creative level design and a great soundtrack",
    "competitive tactical shooter where every round is a puzzle",
    "turn-based RPG with witty writing and lovable companions",
    "laid-back life simulation where I can build a dream home",
    "kart racing with antigravity tracks and easy drifting",
    "realistic football simulation with deep career mode",
]


def embedding_recommendations_ui():
    st.header("AI-Powered Recommendations")
    st.caption(
        "Describe what you want to play, in plain English. We embed your "
        "description and find games whose reviews + descriptions match."
    )

    gamer_id = current_user_id()
    if gamer_id is not None:
        st.caption(f"Filtering out games already in Gamer {gamer_id}'s library.")

    # Seed the textarea from session_state so suggestion clicks can pre-fill it.
    if "embedding_query" not in st.session_state:
        st.session_state.embedding_query = ""

    st.subheader("Try one of these")
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        target_col = cols[i % 2]
        if target_col.button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.embedding_query = suggestion
            st.rerun()

    with st.expander("More ideas (copy-paste)"):
        st.markdown(
            "- **Mood:** *something nostalgic from my childhood*\n"
            "- **Mechanic:** *gravity-bending physics puzzles across mini-worlds*\n"
            "- **Sentiment:** *a game my friends and I keep coming back to for tactical multiplayer*\n"
            "- **Contrast:** *calm and relaxing, not violent*\n"
            "- **Combo:** *open-world Caribbean shooter against a dictator*\n\n"
            "**Tip:** more adjectives = better matches. Embeddings reward specificity."
        )

    query = st.text_area(
        "What kind of game are you in the mood for?",
        value=st.session_state.embedding_query,
        placeholder="e.g. open-world fantasy with deep crafting and a dark story",
        height=100,
        key="embedding_query_input",
    )

    if st.button("Find similar games", type="primary"):
        if not query.strip():
            st.error("Please type a description or click one of the suggestions above.")
            return

        params = {"query": query.strip()}
        if gamer_id is not None:
            params["gamer_id"] = gamer_id

        payload = fetch_raw("get_embedding_recommendations/", params)
        if not payload:
            return
        if payload.get("error"):
            st.error(payload["error"])
            return

        rows = payload.get("data") or []
        advisor_text = payload.get("advisor") or ""

        if not rows:
            st.info(
                "No games matched closely enough. Try a more general "
                "description, or make sure the Chunks table is populated "
                "(run `python API/ingest_embeddings.py`)."
            )
            return

        import pandas as pd
        df = pd.DataFrame(rows)
        df["Similarity"] = (1 - df["Distance"]).round(3)

        st.success(f"{len(df)} match{'es' if len(df) != 1 else ''} found.")

        if advisor_text:
            with st.container(border=True):
                st.markdown("### 🤖 AI Advisor")
                st.markdown(advisor_text)
            st.divider()
            st.markdown("### Raw matches")
        for _, row in df.iterrows():
            with st.container(border=True):
                cols = st.columns([3, 1])
                with cols[0]:
                    st.markdown(
                        f"### {row['GameTitle']}  \n"
                        f"*{row['StudioName']} · {row['YearReleased']} · "
                        f"avg rating {row['AverageRating']}/5*"
                    )
                    st.markdown(f"> {row['Evidence']}")
                with cols[1]:
                    st.metric("Similarity", f"{row['Similarity']:.2%}")
                    st.caption(f"distance {row['Distance']:.3f}")
