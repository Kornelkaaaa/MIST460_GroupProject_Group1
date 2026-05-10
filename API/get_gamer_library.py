from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def get_gamer_library(gamer_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    cursor.execute(
        "SELECT GameID, GameTitle, YearReleased, AverageRating, "
        "PrimaryGenre, HoursPlayed, Status, LibraryID, DateAdded "
        "FROM dbo.fn_GetGamerLibrary(%d) "
        "ORDER BY DateAdded DESC",
        (gamer_id,),
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
            "PrimaryGenre": row["PrimaryGenre"],
            "HoursPlayed": _to_float(row["HoursPlayed"]),
            "Status": row["Status"],
            "LibraryID": row["LibraryID"],
            "DateAdded": row["DateAdded"].isoformat() if row["DateAdded"] is not None else None,
        }
        for row in rows
    ]
    return {"data": results}
