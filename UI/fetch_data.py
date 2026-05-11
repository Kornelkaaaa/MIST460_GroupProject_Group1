from typing import Optional

import pandas as pd
import requests
import streamlit as st


FASTAPI_BASE_URL = "http://localhost:8067"  # Change to deployed API URL when applicable

REQUEST_TIMEOUT = 90  # seconds — generous enough for Azure SQL wake-ups + LLM calls


def _friendly_error(exc: Exception) -> str:
    """Turn raw requests exceptions into something a user can act on."""
    if isinstance(exc, requests.exceptions.ConnectionError):
        return (
            "Couldn't reach the API. Is the FastAPI server running on "
            f"`{FASTAPI_BASE_URL}`?"
        )
    if isinstance(exc, requests.exceptions.Timeout):
        return (
            "The API took too long to respond. Azure SQL Serverless may be "
            "waking up — wait ~60 seconds and try again."
        )
    return f"Unexpected error: {exc}"


def _do_request(endpoint: str, params: dict, method: str):
    url = f"{FASTAPI_BASE_URL}/{endpoint}"
    if method == "GET":
        return requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    return requests.post(url, json=params, timeout=REQUEST_TIMEOUT)


def fetch_data(
    endpoint: str,
    input_params: dict,
    method: str = "GET",
    data_key: str = "data",
    spinner_text: str = "Loading…",
) -> Optional[pd.DataFrame]:
    """Fetch rows from an endpoint and return them as a DataFrame.
    Shows a spinner while waiting and a friendly error on failure."""
    try:
        with st.spinner(spinner_text):
            response = _do_request(endpoint, input_params, method)
    except requests.exceptions.RequestException as e:
        st.error(_friendly_error(e))
        return None

    if response.status_code == 200:
        payload = response.json()
        rows = payload.get(data_key, [])
        return pd.DataFrame(rows)

    st.error(f"API error ({response.status_code}): {response.text[:200]}")
    return None


def fetch_raw(
    endpoint: str,
    input_params: dict,
    method: str = "GET",
    spinner_text: str = "Loading…",
) -> Optional[dict]:
    """Same as fetch_data but returns the raw JSON payload."""
    try:
        with st.spinner(spinner_text):
            response = _do_request(endpoint, input_params, method)
    except requests.exceptions.RequestException as e:
        st.error(_friendly_error(e))
        return None

    if response.status_code == 200:
        return response.json()

    st.error(f"API error ({response.status_code}): {response.text[:200]}")
    return None


def current_user_id() -> Optional[int]:
    val = st.session_state.get("app_user_id")
    return int(val) if val is not None else None


def current_user_name() -> Optional[str]:
    return st.session_state.get("app_user_name")


def current_user_role() -> Optional[str]:
    return st.session_state.get("app_user_role")


def require_login() -> Optional[int]:
    uid = current_user_id()
    if uid is None:
        st.warning("Please log in first using **🔑 Account → Log in / Validate**.")
        return None
    name = current_user_name()
    label = f"{name} (ID: {uid})" if name else f"ID: {uid}"
    st.caption(f"Logged in as {label}")
    return uid


def current_user_id() -> Optional[int]:
    val = st.session_state.get("app_user_id")
    return int(val) if val is not None else None


def current_user_name() -> Optional[str]:
    return st.session_state.get("app_user_name")


def current_user_role() -> Optional[str]:
    return st.session_state.get("app_user_role")


def require_login() -> Optional[int]:
    uid = current_user_id()
    if uid is None:
        st.warning("Please log in first using **Validate User Credentials**.")
        return None
    name = current_user_name()
    label = f"{name} (ID: {uid})" if name else f"ID: {uid}"
    st.caption(f"Logged in as {label}")
    return uid
