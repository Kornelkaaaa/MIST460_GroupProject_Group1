# MIST 460 — Game Recommender (Group 1)

A 3-tier game recommendation system:

- **Data/** — SQL Server schema, programming objects (functions, triggers, procedures), seed data
- **API/** — FastAPI backend that calls the stored procedures via `pymssql`
- **UI/** — Streamlit frontend that consumes the API

---

## Prerequisites

- Python 3.10+
- SQL Server instance with the `MIST_460_Group1` database created and the scripts in `Data/` executed in this order:
  1. `CreateTables_Group1.sql`
  2. `InsertData_Group1.sql`
  3. `DatabaseProgrammingObjects_Group1.sql`

---

## 1. Set up the virtual environment

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

### Windows (Git Bash / cmd)

```bash
# --- API venv ---
cd API
python -m venv .venv
source .venv/Scripts/activate     # Git Bash
# OR: .venv\Scripts\activate.bat  # cmd
pip install -r requirements.txt
deactivate
cd ..

# --- UI venv ---
cd UI
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
deactivate
cd ..
```

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

Inside the `API/` folder, copy the example environment file:

```bash
cd API
cp .env.example .env       # Windows cmd: copy .env.example .env
```

### Option A — run **without a database** (mock mode)

Best when you just want to see the UI + API working end-to-end. Open `.env` and make sure:

```
MOCK_MODE=true
```

That's it — no DB credentials required. All endpoints return canned sample data.

### Option B — run **against the real database**

Edit `.env`:

```
MOCK_MODE=false
DB_SERVER=your-server.database.windows.net
DB_NAME=MIST_460_Group1
DB_USER=your-username
DB_PASSWORD=your-password
```

Verify the connection:

```bash
# from API/ with the API venv activated
python test_get_db_connection.py
```

---

## 3. Run the API

```bash
cd API
# activate the API venv first (see step 1)
uvicorn game_recommender_apis:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

Available endpoints:

| Endpoint | Stored Procedure |
|---|---|
| `GET /validate_user/` | `procValidateUser` |
| `GET /get_recommendations/` | `sp_GetRecommendations` |
| `GET /search_games_by_keyword/` | `sp_SearchGamesByKeyword` |
| `GET /get_next_game_suggestion/` | `sp_GetNextGameSuggestion` |
| `GET /get_developer_analytics/` | `sp_GetDeveloperAnalytics` |

---

## 4. Run the UI

In a **separate terminal**:

```bash
cd UI
# activate the UI venv first (see step 1)
streamlit run game_recommender_ui.py
```

Streamlit opens at `http://localhost:8501`.

If your API is running somewhere other than `http://localhost:8000`, update `FASTAPI_BASE_URL` at the top of `UI/fetch_data.py`.

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
│   ├── validate_user.py
│   ├── get_recommendations.py
│   ├── search_games_by_keyword.py
│   ├── get_next_game_suggestion.py
│   ├── get_developer_analytics.py
│   └── game_recommender_apis.py
└── UI/
    ├── requirements.txt
    ├── fetch_data.py
    ├── validate_user_ui.py
    ├── get_recommendations_ui.py
    ├── search_games_ui.py
    ├── get_next_game_suggestion_ui.py
    ├── get_developer_analytics_ui.py
    └── game_recommender_ui.py
```
