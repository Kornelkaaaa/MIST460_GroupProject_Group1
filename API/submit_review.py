from typing import Optional

import pymssql

from get_db_connection import get_db_connection


def submit_review(
    gamer_id: int,
    game_title: str,
    rating: float,
    review_text: Optional[str] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        cursor.execute(
            "EXEC sp_SubmitReview "
            "@GamerID=%d, @GameTitle=%s, @Rating=%s, @ReviewText=%s",
            (gamer_id, game_title, rating, review_text),
        )
        rows = cursor.fetchall()
        conn.commit()
    except pymssql.Error as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}

    conn.close()

    return {"data": rows[0] if rows else {}}
