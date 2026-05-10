from typing import Any, Optional

import pymssql

from get_db_connection import get_db_connection


def _to_float(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def get_recommendations(gamer_id: int, top_n: int = 6):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("EXEC sp_GetRecommendations %d, %d", (gamer_id, top_n))

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
            "CommunityCompletionPct": _to_float(row["CommunityCompletionPct"]),
            "RecommendationReason": row["RecommendationReason"],
        }
        for row in rows
    ]
    return {"data": results}
