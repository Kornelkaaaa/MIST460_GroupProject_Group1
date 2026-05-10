from typing import Optional

import pymssql

from get_db_connection import get_db_connection


def search_games_by_keyword(keyword: str, gamer_id: Optional[int] = None, top_n: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute(
        "EXEC sp_SearchGamesByKeyword %s, %s, %d",
        (keyword, gamer_id, top_n),
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
            "GameDescription": row["GameDescription"],
            "YearReleased": row["YearReleased"],
            "AverageRating": float(row["AverageRating"]) if row["AverageRating"] is not None else None,
            "StudioName": row["StudioName"],
            "PrimaryGenre": row["PrimaryGenre"],
            "CompletionRatePct": float(row["CompletionRatePct"]) if row["CompletionRatePct"] is not None else None,
            "AlreadyOwned": row["AlreadyOwned"],
        }
        for row in rows
    ]
    return {"data": results}
