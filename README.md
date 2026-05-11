# MIST 460 — Game Recommender (Group 1)

A 3-tier game recommendation system with **classical SQL recommendations** and **AI-powered semantic search** over user reviews + game descriptions:

- **Data/** — SQL Server schema, programming objects (functions, triggers, procedures), seed data
- **API/** — FastAPI backend that calls the stored procedures via `pymssql`; also handles OpenAI embeddings + LLM advisor
- **UI/** — Streamlit frontend organized into sections (Account / Library / Discover / Reviews)

---

## What it can do

**Gamers can:**
- Sign up, log in, edit their profile, view their game library + play stats
- Add games, remove games, update play status (Not Started / In Progress / Completed / Abandoned), log hours
- Submit, edit, and delete reviews
- Search the catalog by keyword
- Get **AI-powered recommendations** — describe a vibe in plain English; the app embeds the query, runs a cosine-similarity vector search over review + description chunks, and an LLM advisor ranks + explains the results

**Developers can:**
- View per-game analytics for their studio: ownership counts, completion rates, sentiment buckets, player-profile breakdowns

---

## Prerequisites

- Python 3.10+
- An Azure SQL Database (or SQL Server 2025+) with the `VECTOR` type available. The database name in this repo is `mist460-api-group1`.
- An OpenAI API key (used for embeddings + the LLM advisor)
- The three SQL scripts in `Data/` executed in order:
  1. `CreateTables_Group1.sql`
  2. `InsertData_Group1.sql`
  3. `DatabaseProgrammingObjects_Group1.sql`

> Re-running any of these is idempotent (`DROP TABLE IF EXISTS` / `DROP PROCEDURE IF EXISTS` at the top of each script). Re-run all three after any schema change.

---

## 1. Set up the virtual environments

We use **two separate venvs** — one for the API and one for the UI — so the dependencies stay isolated.

### Windows (PowerShell)

```powershell
# --- API venv ---
cd API
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
deactivate
cd ..

# --- UI venv ---
cd UI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
deactivate
cd ..
```

> If PowerShell blocks the activation script, run once:
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

> **Windows path-length warning.** If your repo lives under a long path (e.g. `Documents\West Virginia University\Senior year\…`) the UI venv install can fail with `[WinError 206] The filename or extension is too long`. Two fixes:
>
> 1. **Enable long paths** (admin PowerShell, one-time): `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force`, then reopen PowerShell.
> 2. **Or put the UI venv at a short path:** `python -m venv C:\v\mist460` and activate it with `& C:\v\mist460\Scripts\Activate.ps1` instead of the in-repo one.

### macOS / Linux

```bash
# --- API venv ---
cd API
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# --- UI venv ---
cd UI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..
```

---

## 2. Configure the API

Inside `API/`, copy the example environment file and fill in your credentials:

```bash
cd API
cp .env.example .env       # Windows cmd: copy .env.example .env
```

Edit `.env`:

```
DB_SERVER=your-server.database.windows.net
DB_NAME=mist460-api-group1
DB_USER=your-username
DB_PASSWORD=your-password
OPENAI_API_KEY=sk-...
```

Verify the connection:

```bash
# from API/ with the API venv activated
python test_get_db_connection.py
```

> **Azure SQL note.** If your database is on the Azure SQL Serverless tier, the first request after a long pause may fail with error `40613` ("not currently available"). Wait ~60 seconds and retry — Azure auto-resumes the database on demand.

---

## 3. Populate the embeddings (one-time + after each re-seed)

The AI recommendations feature requires the `Chunks` table to contain OpenAI embeddings of every game description and review. Run the ingestion script:

```bash
# from API/ with the API venv activated
python ingest_embeddings.py
```

It truncates `Chunks`, embeds every `GameDescription` and `GamerReview.ReviewText` using OpenAI `text-embedding-3-small` (1536 dimensions), and re-inserts them with their `GameID`. Total cost for the seed data is well under $0.01.

> **Permissions note.** `APIUser` needs `SELECT, INSERT, DELETE` on `dbo.Chunks`. `CreateTables_Group1.sql` issues that GRANT when run by an admin account. If you bypassed the grant, run this once in SSMS as your admin user:
>
> ```sql
> GRANT SELECT, INSERT, DELETE ON dbo.Chunks TO APIUser;
> ```

---

## 4. Run the API

```bash
cd API
# activate the API venv first
uvicorn game_recommender_apis:app --reload --port 8067
```

The API runs at `http://localhost:8067`. Interactive docs: `http://localhost:8067/docs`.

### Endpoints

**Read endpoints (GET):**

| Endpoint | What it does |
|---|---|
| `GET /validate_user/` | Email + password authentication; returns `AppUserID`, `Fullname`, `UserRole` |
| `GET /get_recommendations/` | Classical SQL recommendations from `sp_GetRecommendations` |
| `GET /search_games_by_keyword/` | Title / description / studio / genre LIKE search |
| `GET /get_next_game_suggestion/` | Priority-based suggestion (unstarted → in-progress → catalog fallback) |
| `GET /get_developer_analytics/` | 3 result sets: summary, sentiment, player profile |
| `GET /get_gamer_library/` | Every game in a gamer's library with stats |
| `GET /get_all_games/` | Full catalog (for "Add a game" dropdown) |
| `GET /get_developer_games/` | Games belonging to a developer (for analytics dropdown) |
| `GET /get_gamer_profile/` | Read a gamer's profile (for the edit form) |
| `GET /get_embedding_recommendations/` | **AI recommendations** — embed query, vector search, LLM advisor explanation |

**Action endpoints (GET; mutate data):**

| Endpoint | What it does |
|---|---|
| `GET /register_gamer/` | Create AppUser + Gamer row |
| `GET /full_gamer_onboarding/` | Register + add owned games + return first recommendations |
| `GET /add_game_to_library/` | Insert a Library row; trigger seeds the PlayerStats row |
| `GET /remove_game_from_library/` | Delete a Library row (PlayerStats cascades; reviews are preserved) |
| `GET /update_game_status/` | Change status / hours played |
| `GET /submit_review/` | Insert a review; trigger recalcs `Game.AverageRating` |
| `GET /update_review/` | Update an existing review |
| `GET /delete_review/` | Delete a review |
| `GET /update_gamer_profile/` | Edit profile fields (COALESCE pattern: nulls keep existing values) |

---

## 5. Run the UI

In a **separate terminal**:

```bash
cd UI
# activate the UI venv first
streamlit run game_recommender_ui.py
```

Streamlit opens at `http://localhost:8501`.

If your API is running somewhere other than `http://localhost:8067`, update `FASTAPI_BASE_URL` at the top of `UI/fetch_data.py`.

### UI features

- **Sidebar sections** grouped by purpose:
  - 🏠 Home — welcome / landing page
  - 🔑 Account — log in, sign up, edit profile
  - 📚 Library — view library, add/remove games, update status
  - ✨ Discover — AI recommendations, keyword search
  - ⭐ Reviews — submit / edit / delete reviews
  - 📊 Studio (developers only) — analytics
- **Login banner** — sidebar always shows "Logged in as **Name** · Role · ID `X`" or "Not logged in" with a one-click logout
- **Role-based menu** — developers see only the analytics page; gamers see only gamer features
- **Auto-fill of gamer/developer ID** — once logged in, every page picks it up from session state
- **Searchable game dropdowns** — anywhere a title is needed, Streamlit shows a type-to-filter selectbox populated from the catalog or your library
- **Card layouts** with metrics, icons (✅ Completed · 🎮 In Progress · ⏳ Not Started · ❌ Abandoned), and inline reviews/evidence
- **Spinners + friendly errors** — every API call shows a spinner; connection refused and timeout errors are translated to actionable messages
- **AI Recommendations page** — suggestion chips, free-text input, AI Advisor markdown block above the raw match cards

### Test credentials

Seeded by `Data/InsertData_Group1.sql`. Plaintext passwords are listed; the database stores `HASHBYTES('SHA2_256', N'<pwd>')`.

| Role | Email | Password |
|---|---|---|
| Gamer | `alex.rivera@email.com` | `alex123` |
| Gamer | `jordan.kim@email.com` | `jordan456` |
| Gamer | `morgan.patel@email.com` | `morgan789` |
| Gamer | `taylor.nguyen@email.com` | `taylor321` |
| Gamer | `casey.johnson@email.com` | `casey654` |
| Developer | `bobby.kotick@activision.com` | `act111` |
| Developer | `andrew.wilson@ea.com` | `ea222` |
| Developer | `yves.g@ubisoft.com` | `ubi333` |
| Developer | `shigeru.miyamoto@nintendo.com` | `nin444` |

---

## How the AI recommendations work

```
User types a query like "colorful platformer to play with my kids"
                  │
                  ▼
1) OpenAI text-embedding-3-small embeds the query (1536-dim vector)
                  │
                  ▼
2) SQL Server vector search via fnGetGameRecommendationsByReview(@v)
   ├─ scans Chunks (review + description embeddings)
   ├─ groups by GameID, picks each game's closest chunk by cosine distance
   └─ returns TOP 5 games with distance ≤ 0.6
                  │
                  ▼
3) sp_GetEmbeddingRecommendations enriches with Game/Developer info,
   filters out games the gamer already owns
                  │
                  ▼
4) Python wrapper calls gpt-4o-mini with temperature=0:
   - system prompt = "expert game advisor"
   - human prompt = original query + retrieved context
   - advisor ranks games, flags weak matches (distance > 0.4), explains
                  │
                  ▼
5) UI shows the AI advisor markdown above the raw match cards
```

**Cost per query:** ~$0.0002 (one tiny embedding call + one short chat completion).
**`temperature=0`** means identical query → identical advisor response, useful for screenshots and report deliverables.

---

## Project layout

```
.
├── Data/
│   ├── CreateTables_Group1.sql
│   ├── InsertData_Group1.sql
│   └── DatabaseProgrammingObjects_Group1.sql
├── API/
│   ├── .env.example
│   ├── requirements.txt
│   ├── startup.sh
│   ├── get_db_connection.py
│   ├── test_get_db_connection.py
│   ├── ingest_embeddings.py            # one-time embedding population
│   ├── game_advisor.py                  # OpenAI advisor (system+human prompts)
│   ├── game_recommender_apis.py         # FastAPI routes
│   ├── validate_user.py
│   ├── register_gamer.py
│   ├── full_gamer_onboarding.py
│   ├── update_gamer_profile.py
│   ├── get_gamer_profile.py
│   ├── get_gamer_library.py
│   ├── get_all_games.py
│   ├── get_developer_games.py
│   ├── add_game_to_library.py
│   ├── remove_game_from_library.py
│   ├── update_game_status.py
│   ├── submit_review.py
│   ├── update_review.py
│   ├── delete_review.py
│   ├── search_games_by_keyword.py
│   ├── get_recommendations.py
│   ├── get_embedding_recommendations.py
│   ├── get_next_game_suggestion.py
│   └── get_developer_analytics.py
└── UI/
    ├── requirements.txt
    ├── fetch_data.py                    # shared helpers + spinners + login state
    ├── game_recommender_ui.py           # sidebar + page routing
    ├── welcome_ui.py
    ├── validate_user_ui.py
    ├── full_gamer_onboarding_ui.py
    ├── update_gamer_profile_ui.py
    ├── get_gamer_library_ui.py
    ├── add_game_to_library_ui.py
    ├── remove_game_from_library_ui.py
    ├── update_game_status_ui.py
    ├── submit_review_ui.py
    ├── manage_reviews_ui.py
    ├── search_games_ui.py
    ├── embedding_recommendations_ui.py
    └── get_developer_analytics_ui.py
```

---

## Architecture notes

### SQL programming objects (`Data/DatabaseProgrammingObjects_Group1.sql`)

Four-layer hierarchy:

- **Layer 1 — Functions** (pure logic, no side effects)
  - `fn_GamerExists`, `fn_GameExists`, `fn_GamerOwnsGame`, `fn_GamerAlreadyReviewed`
  - `fn_GetGameAverageRating`, `fn_GetGameCompletionRate`, `fn_GetGamerCompletedCount`, `fn_GetTotalHoursPlayed`
  - `fn_GetTopGenreForGame`, `fn_GetGameIDByTitle`
  - `fn_GetGamerLibrary` (table-valued, fully inlinable)
  - `fnGetGameRecommendationsByReview` (vector search via `Vector_Distance('cosine', …)`)
- **Layer 2 — Triggers**
  - `trg_GamerReview_RecalcRating` (keeps `Game.AverageRating` in sync after INSERT/UPDATE/DELETE)
  - `trg_AutoInitPlayerStats` (auto-creates a PlayerStats row when a Library row is inserted)
  - `trg_BlockFinishedGameStatusChange` (prevents rollback from Completed → earlier state)
- **Layer 3 — Single-action procedures** — wrappers exposed to the API
- **Layer 4 — Orchestration procedures**
  - `sp_FullGamerOnboarding` (register + add owned games + return recommendations in one transaction)
  - `sp_GetNextGameSuggestion` (priority chain: unstarted → in-progress → catalog)
  - `sp_GetDeveloperAnalytics` (3 result sets via CTEs to avoid cartesian-product over reviews)

### Vector search

The `Chunks` table stores `VECTOR(1536)` embeddings of every game description and review chunk. `fnGetGameRecommendationsByReview` runs cosine distance over those vectors via SQL Server's native `Vector_Distance` function, returning the top-5 games whose closest chunk is within distance ≤ 0.6.

### Password storage

`procValidateUser` and the seed data both use `HASHBYTES('SHA2_256', …)`. Plaintext is never stored.

### Schema decisions worth knowing

- `PlayerStats` is keyed by `LibraryID` only (not LibraryID + GameID). The game is implied by `Library.GameID` — removing the redundant column eliminated a class of "forgot to populate GameID" insert bugs.
- `trg_PreventDuplicateLibraryEntry` was removed because INSTEAD OF triggers break `SCOPE_IDENTITY()`. Duplicate prevention is now handled by `UK_Library_GamerGame UNIQUE (GamerID, GameID)`.
- Game status vocabulary: `'Not Started' | 'In Progress' | 'Completed' | 'Abandoned'` (enforced by a CHECK constraint on `PlayerStats.Status`).
- `Genre.GenreName` and `Gamer.PreferredGenres` both use canonical full names (`First-Person Shooter`, not `FPS`). `sp_GetRecommendations` parses the gamer's `PreferredGenres` via `STRING_SPLIT` and joins to `Genre` for exact-match recommendations, with a top-rated-unowned fallback.
