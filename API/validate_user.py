import pymssql

from get_db_connection import get_db_connection


def validate_user(username: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor(as_dict=True)
    cursor.execute("EXEC procValidateUser %s, %s", (username, password))

    try:
        rows = cursor.fetchall()
    except pymssql.Error:
        rows = []

    conn.close()

    results = [
        {
            "AppUserID": row["AppUserID"],
            "Fullname": row["Fullname"],
        }
        for row in rows
    ]
    return {"data": results}
