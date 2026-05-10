from typing import Optional

import pymssql

from get_db_connection import get_db_connection


def register_gamer(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: Optional[str] = None,
    preferred_genres: Optional[str] = None,
    preferred_difficulty: Optional[str] = None,
    preferred_play_style: Optional[str] = None,
    preferred_mode: Optional[str] = None,
    available_play_time: Optional[float] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    sql = """
        DECLARE @NewID INT;
        EXEC sp_RegisterGamer
            @FirstName           = %s,
            @LastName            = %s,
            @Email               = %s,
            @PasswordHash        = HASHBYTES('SHA2_256', %s),
            @Phone               = %s,
            @PreferredGenres     = %s,
            @PreferredDifficulty = %s,
            @PreferredPlayStyle  = %s,
            @PreferredMode       = %s,
            @AvailablePlayTime   = %s,
            @NewGamerID          = @NewID OUTPUT;
        SELECT @NewID AS NewGamerID;
    """
    params = (
        first_name,
        last_name,
        email,
        password,
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

    new_id = rows[0]["NewGamerID"] if rows else None
    return {"data": {"NewGamerID": new_id}}
