from get_db_connection import get_db_connection


def main():
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)

    cur.execute(
        "SELECT @@SERVERNAME AS Server, DB_NAME() AS DbName, "
        "SUSER_SNAME() AS LoginAs, GETDATE() AS Now"
    )
    print("API CONNECTION TARGET:")
    for row in cur.fetchall():
        print(f"  Server:  {row['Server']}")
        print(f"  DB:      {row['DbName']}")
        print(f"  Login:   {row['LoginAs']}")
        print(f"  Now:     {row['Now']}")

    cur.execute(
        "SELECT name, modify_date FROM sys.procedures "
        "WHERE name = 'sp_GetRecommendations'"
    )
    row = cur.fetchone()
    print("\nsp_GetRecommendations in this DB:")
    if row:
        print(f"  exists — last modified {row['modify_date']}")
    else:
        print("  NOT FOUND")

    print("\nEXEC sp_GetRecommendations @GamerID=1, @TopN=6:")
    try:
        cur.execute("EXEC sp_GetRecommendations %d, %d", (1, 6))
        rows = cur.fetchall()
        print(f"  {len(rows)} row(s) returned")
        for r in rows:
            print(
                f"    GameID={r.get('GameID')}  "
                f"{r.get('GameTitle')!r}  "
                f"genre={r.get('PrimaryGenre')!r}  "
                f"reason={r.get('RecommendationReason')!r}"
            )
    except Exception as e:
        print(f"  ERROR: {e}")

    cur.execute("SELECT GamerID, PreferredGenres FROM Gamer ORDER BY GamerID")
    print("\nGamer.PreferredGenres in this DB:")
    for row in cur.fetchall():
        print(f"  Gamer {row['GamerID']}: {row['PreferredGenres']}")

    conn.close()


if __name__ == "__main__":
    main()
