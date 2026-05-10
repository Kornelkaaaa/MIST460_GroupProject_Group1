from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def get_developer_games(developer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    cursor.execute(
        "SELECT GameID, GameTitle, YearReleased, AverageRating "
        "FROM Game "
        "WHERE DeveloperID = %d "
        "ORDER BY GameTitle",
        (developer_id,),
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
        }
        for row in rows
    ]
    return {"data": results}
