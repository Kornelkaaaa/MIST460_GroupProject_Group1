from typing import List, Optional

import pymssql

from get_db_connection import get_db_connection


def full_gamer_onboarding(
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
    owned_game_titles: Optional[str] = None,
):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)

    sql = """
        EXEC sp_FullGamerOnboarding
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
            @OwnedGameTitles     = %s;
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
        owned_game_titles,
    )

    recommendations: List[dict] = []
    confirmation: dict = {}

    try:
        cursor.execute(sql, params)

        try:
            recommendations = cursor.fetchall()
        except pymssql.Error:
            recommendations = []

        if cursor.nextset():
            try:
                rows = cursor.fetchall()
                confirmation = rows[0] if rows else {}
            except pymssql.Error:
                confirmation = {}

        conn.commit()
    except pymssql.Error as e:
        conn.rollback()
        conn.close()
        return {"error": str(e)}

    conn.close()

    return {
        "data": {
            "confirmation": confirmation,
            "recommendations": recommendations,
        }
    }
