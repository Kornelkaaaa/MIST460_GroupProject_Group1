from get_db_connection import get_db_connection


def main():
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)

    for kw in ("mario", "FPS", "open world", "action"):
        print(f"\n=== EXEC sp_SearchGamesByKeyword @Keyword='{kw}', @GamerID=1, @TopN=10 ===")
        try:
            cur.execute("EXEC sp_SearchGamesByKeyword %s, %s, %d", (kw, 1, 10))
            rows = cur.fetchall()
            print(f"  {len(rows)} row(s)")
            for r in rows:
                print(
                    f"    {r.get('GameID'):>3}  {r.get('GameTitle')!r:<40}  "
                    f"{r.get('PrimaryGenre')!r:<22}  owned={r.get('AlreadyOwned')!r}"
                )
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}: {e}")

    conn.close()


if __name__ == "__main__":
    main()
