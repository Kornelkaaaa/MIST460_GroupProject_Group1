import streamlit as st

from fetch_data import fetch_data


def validate_user_ui():
    st.header("Validate User Credentials")

    if st.session_state.get("app_user_id"):
        st.info(
            f"You are already logged in as "
            f"**{st.session_state.get('app_user_name', '?')}** "
            f"(ID: {st.session_state['app_user_id']}). "
            f"Use the sidebar to log out."
        )
        return

    username = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Validate Credentials"):
        if not username.strip():
            st.error("Email is required.")
            return
        if not password.strip():
            st.error("Password is required.")
            return

        df = fetch_data(
            "validate_user/",
            {"username": username.strip(), "password": password.strip()},
        )

        if df is not None and not df.empty:
            app_user_id = int(df["AppUserID"].values[0])
            fullname = str(df["Fullname"].values[0])
            role = str(df["UserRole"].values[0]) if "UserRole" in df.columns else "Gamer"
            st.session_state.app_user_id = app_user_id
            st.session_state.app_user_name = fullname
            st.session_state.app_user_role = role
            st.success(f"Welcome, {fullname}! (Role: {role})")
            st.rerun()
        else:
            st.info("Invalid email or password.")
