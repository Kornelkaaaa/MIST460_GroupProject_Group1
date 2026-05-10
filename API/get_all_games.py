from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def get_all_games():
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    cursor.execute(
        "SELECT g.GameID, g.GameTitle, g.YearReleased, g.AverageRating, "
        "       d.StudioName, "
        "       dbo.fn_GetTopGenreForGame(g.GameID) AS PrimaryGenre "
        "FROM Game g "
        "JOIN Developer d ON g.DeveloperID = d.DeveloperID "
        "ORDER BY g.GameTitle"
    )

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    results = [
        {
            "GameID": row["GameID"],
            "GameTitle": row["GameTitle"],
            "YearReleased": row["YearReleased"],
            "AverageRating": _to_float(row["AverageRating"]),
            "StudioName": row["StudioName"],
            "PrimaryGenre": row["PrimaryGenre"],
        }
        for row in rows
    ]
    return {"data": results}
