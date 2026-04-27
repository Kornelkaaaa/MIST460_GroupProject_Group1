import pymssql

from get_db_connection import get_db_connection
from mock_data import RECOMMENDATIONS, is_mock_mode


def get_recommendations(gamer_id: int, top_n: int = 6):
    if is_mock_mode():
        return {"data": RECOMMENDATIONS[:top_n]}

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
            "AverageRating": float(row["AverageRating"]) if row["AverageRating"] is not None else None,
            "StudioName": row["StudioName"],
            "PrimaryGenre": row["PrimaryGenre"],
            "CommunityCompletionPct": float(row["CommunityCompletionPct"]) if row["CommunityCompletionPct"] is not None else None,
            "RecommendationReason": row["RecommendationReason"],
        }
        for row in rows
    ]
    return {"data": results}
