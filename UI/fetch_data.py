from typing import Optional

import pandas as pd
import requests
import streamlit as st


FASTAPI_BASE_URL = "http://localhost:8067"  # Change to deployed API URL when applicable


def fetch_data(
    endpoint: str,
    input_params: dict,
    method: str = "GET",
    data_key: str = "data",
) -> Optional[pd.DataFrame]:
    if method == "GET":
        response = requests.get(f"{FASTAPI_BASE_URL}/{endpoint}", params=input_params)
    else:
        response = requests.post(f"{FASTAPI_BASE_URL}/{endpoint}", json=input_params)

    if response.status_code == 200:
        payload = response.json()
        rows = payload.get(data_key, [])
        return pd.DataFrame(rows)

    st.error(f"Error fetching data: {response.status_code} - {response.text}")
    return None


def fetch_raw(
    endpoint: str,
    input_params: dict,
    method: str = "GET",
) -> Optional[dict]:
    if method == "GET":
        response = requests.get(f"{FASTAPI_BASE_URL}/{endpoint}", params=input_params)
    else:
        response = requests.post(f"{FASTAPI_BASE_URL}/{endpoint}", json=input_params)

    if response.status_code == 200:
        return response.json()

    st.error(f"Error fetching data: {response.status_code} - {response.text}")
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
        st.warning("Please log in first using **Validate User Credentials**.")
        return None
    name = current_user_name()
    label = f"{name} (ID: {uid})" if name else f"ID: {uid}"
    st.caption(f"Logged in as {label}")
    return uid
