# MIST 460 — Game Recommender (Group 1)

A 3-tier game recommendation system:

- **Data/** — SQL Server schema, programming objects (functions, triggers, procedures), seed data
- **API/** — FastAPI backend that calls the stored procedures via `pymssql`
- **UI/** — Streamlit frontend that consumes the API

---

## Prerequisites

- Python 3.10+
- A SQL Server instance with the `mist460-api-group1` database created and the scripts in `Data/` executed in this order:
  1. `CreateTables_Group1.sql`
  2. `InsertData_Group1.sql`
  3. `DatabaseProgrammingObjects_Group1.sql`

> If you change any of the SQL files, **re-run all three** in the same order so the database, seed data, and procs stay in sync.

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

Inside the `API/` folder, copy the example environment file and fill in your DB credentials:

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
```

Verify the connection:

```bash
# from API/ with the API venv activated
python test_get_db_connection.py
```

> **Azure SQL note.** If your database is on the Azure SQL Serverless tier, the first request after a long pause may fail with error `40613` ("not currently available"). Wait ~60 seconds and retry — Azure auto-resumes the database on demand.

---

## 3. Run the API

```bash
cd API
# activate the API venv first (see step 1)
uvicorn game_recommender_apis:app --reload --port 8067
```

The API runs at `http://localhost:8067`. Interactive docs: `http://localhost:8067/docs`.

### Endpoints

**Read endpoints (GET):**

| Endpoint | Stored procedure / function |
|---|---|
| `GET /validate_user/` | `procValidateUser` |
| `GET /get_recommendations/` | `sp_GetRecommendations` |
| `GET /search_games_by_keyword/` | `sp_SearchGamesByKeyword` |
| `GET /get_next_game_suggestion/` | `sp_GetNextGameSuggestion` |
| `GET /get_developer_analytics/` | `sp_GetDeveloperAnalytics` |
| `GET /get_gamer_library/` | `fn_GetGamerLibrary` (TVF) |
| `GET /get_all_games/` | direct SELECT on Game |
| `GET /get_developer_games/` | direct SELECT on Game |

**Action endpoints (also GET — they mutate data; method chosen for Streamlit-friendliness):**

| Endpoint | Stored procedure |
|---|---|
| `GET /register_gamer/` | `sp_RegisterGamer` |
| `GET /full_gamer_onboarding/` | `sp_FullGamerOnboarding` |
| `GET /add_game_to_library/` | `sp_AddGameToLibrary` |
| `GET /update_game_status/` | `sp_UpdateGameStatus` |
| `GET /submit_review/` | `sp_SubmitReview` |

---

## 4. Run the UI

In a **separate terminal**:

```bash
cd UI
# activate the UI venv first
streamlit run game_recommender_ui.py
```

Streamlit opens at `http://localhost:8501`.

If your API is running somewhere other than `http://localhost:8067`, update `FASTAPI_BASE_URL` at the top of `UI/fetch_data.py`.

### UI features

- **Login state** is kept in `st.session_state` (`app_user_id`, `app_user_name`, `app_user_role`). The sidebar shows who's logged in and offers a Logout button.
- **Role-based menu.** The sidebar shows different pages depending on the logged-in user's role:
  - **Gamer / not logged in:** Validate User Credentials, Sign Up, My Library & Stats, Get Game Recommendations, Search Games by Keyword, What Should I Play Next?, Add Game to Library, Update Game Status, Submit a Review.
  - **Developer:** Validate User Credentials, Developer Analytics.
- **Auto-fill IDs.** Once you log in, every page that needs your gamer or developer ID picks it up from session state — no manual entry.
- **Searchable game dropdowns.** Anywhere a game title is needed, Streamlit shows a type-to-filter `selectbox` populated from the catalog or your library, so you don't have to remember exact titles.

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
│   ├── game_recommender_apis.py
│   ├── validate_user.py
│   ├── get_recommendations.py
│   ├── search_games_by_keyword.py
│   ├── get_next_game_suggestion.py
│   ├── get_developer_analytics.py
│   ├── get_gamer_library.py
│   ├── get_all_games.py
│   ├── get_developer_games.py
│   ├── register_gamer.py
│   ├── full_gamer_onboarding.py
│   ├── add_game_to_library.py
│   ├── update_game_status.py
│   └── submit_review.py
└── UI/
    ├── requirements.txt
    ├── fetch_data.py
    ├── game_recommender_ui.py
    ├── validate_user_ui.py
    ├── full_gamer_onboarding_ui.py
    ├── get_gamer_library_ui.py
    ├── get_recommendations_ui.py
    ├── search_games_ui.py
    ├── get_next_game_suggestion_ui.py
    ├── add_game_to_library_ui.py
    ├── update_game_status_ui.py
    ├── submit_review_ui.py
    └── get_developer_analytics_ui.py
```

---

## Architecture notes

- **Layered SQL programming objects** (`Data/DatabaseProgrammingObjects_Group1.sql`):
  - **Layer 1** — pure functions (`fn_GamerExists`, `fn_GetTopGenreForGame`, `fn_GetGameAverageRating`, `fn_GetGameCompletionRate`, `fn_GetGamerLibrary`, …)
  - **Layer 2** — triggers (`trg_GamerReview_RecalcRating`, `trg_PreventDuplicateLibraryEntry`, …)
  - **Layer 3** — single-purpose procedures (`sp_RegisterGamer`, `sp_AddGameToLibrary`, `sp_GetRecommendations`, …)
  - **Layer 4** — orchestration procedures that compose Layer 3 (`sp_FullGamerOnboarding`, `sp_GetNextGameSuggestion`, `sp_GetDeveloperAnalytics`)
- **Password storage:** `procValidateUser` and the seed data both use `HASHBYTES('SHA2_256', …)`. Plaintext is never stored.
- **Recommendations matching:** `sp_GetRecommendations` parses the gamer's `PreferredGenres` with `STRING_SPLIT`, joins against the `Genre` table for exact matches, deduplicates via a `@Matched` table variable, and falls back to top-rated unowned games when no preferences match.
- **Game status vocabulary:** `'Not Started' | 'In Progress' | 'Completed' | 'Abandoned'` (enforced by a CHECK constraint on `PlayerStats.Status`).
