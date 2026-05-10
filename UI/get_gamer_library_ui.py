import pandas as pd
import streamlit as st

from fetch_data import fetch_data, require_login


def get_gamer_library_ui():
    st.header("My Library & Stats")

    gamer_id = require_login()
    if gamer_id is None:
        return

    df = fetch_data("get_gamer_library/", {"gamer_id": gamer_id})

    if df is None:
        return

    if df.empty:
        st.info("Your library is empty. Add a game to get started.")
        return

    total_games = len(df)
    total_hours = float(df["HoursPlayed"].fillna(0).sum())
    completed = int((df["Status"] == "Completed").sum())
    in_progress = int((df["Status"] == "In Progress").sum())
    not_started = int((df["Status"] == "Not Started").sum())
    abandoned = int((df["Status"] == "Abandoned").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Games owned", total_games)
    c2.metric("Total hours", f"{total_hours:,.1f}")
    c3.metric("Completed", completed)
    c4.metric("In progress", in_progress)

    st.caption(
        f"Not started: {not_started}  •  Abandoned: {abandoned}"
    )

    status_filter = st.multiselect(
        "Filter by status",
        options=["Not Started", "In Progress", "Completed", "Abandoned"],
        default=[],
    )
    if status_filter:
        df = df[df["Status"].isin(status_filter)]

    st.dataframe(df, use_container_width=True, hide_index=True)
