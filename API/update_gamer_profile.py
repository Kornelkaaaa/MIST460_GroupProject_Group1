from typing import Optional

import pymssql

from get_db_connection import get_db_connection


def update_gamer_profile(
    gamer_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    phone: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    preferred_play_style: Optional[str] = None,
    preferred_mode: Optional[str] = None,
    available_play_time: Optional[float] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    sql = (
        "EXEC sp_UpdateGamerProfile "
        "@GamerID=%d, "
        "@FirstName=%s, @LastName=%s, @Phone=%s, "
        "@PreferredGenres=%s, @PreferredDifficulty=%s, "
        "@PreferredPlayStyle=%s, @PreferredMode=%s, "
        "@AvailablePlayTime=%s"
    )
    params = (
        gamer_id,
        first_name,
        last_name,
        phone,
        preferred_genres,
        preferred_difficulty,
        preferred_play_style,
        preferred_mode,
        available_play_time,
    )

    try:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.commit()
    except pymssql.Error as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}

    conn.close()
    return {"data": rows[0] if rows else {}}
