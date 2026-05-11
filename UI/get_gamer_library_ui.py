import pandas as pd
import streamlit as st

from fetch_data import fetch_data, require_login


STATUS_ICONS = {
    "Completed": "✅",
    "In Progress": "🎮",
    "Not Started": "⏳",
    "Abandoned": "❌",
}


def get_gamer_library_ui():
    st.header("📚 My Library & Stats")

    gamer_id = require_login()
    if gamer_id is None:
        return

    df = fetch_data(
        "get_gamer_library/",
        {"gamer_id": gamer_id},
        spinner_text="Loading your library…",
    )

    if df is None:
        return

    if df.empty:
        st.info("Your library is empty.")
        st.markdown(
            "Head to **📚 Library → Add a game** to pick something from the catalog."
        )
        return

    # ─── Top stats ───
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
    st.caption(f"⏳ Not started: {not_started}  ·  ❌ Abandoned: {abandoned}")

    st.divider()

    # ─── Filter chips ───
    status_filter = st.multiselect(
        "Filter by status",
        options=["Not Started", "In Progress", "Completed", "Abandoned"],
        default=[],
        placeholder="Show all statuses",
    )
    view = df
    if status_filter:
        view = view[view["Status"].isin(status_filter)]

    if view.empty:
        st.info("No games match the selected filters.")
        return

    # ─── Card grid ───
    for _, row in view.iterrows():
        icon = STATUS_ICONS.get(row.get("Status", ""), "🎮")
        with st.container(border=True):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.markdown(
                    f"### {row.get('GameTitle', '?')}  \n"
                    f"*{row.get('PrimaryGenre', '?')} · {row.get('YearReleased', '?')} · "
                    f"avg rating {row.get('AverageRating', '?')}/5*"
                )
                date_added = row.get("DateAdded")
                if isinstance(date_added, str):
                    date_label = date_added.split("T")[0]
                elif date_added is not None:
                    date_label = pd.to_datetime(date_added).strftime("%Y-%m-%d")
                else:
                    date_label = "?"
                st.caption(f"Added to library on {date_label}")
            with cols[1]:
                st.metric("Status", f"{icon} {row.get('Status', '?')}")
            with cols[2]:
                hours = row.get("HoursPlayed")
                st.metric("Hours", f"{float(hours):.1f}" if hours is not None else "—")
