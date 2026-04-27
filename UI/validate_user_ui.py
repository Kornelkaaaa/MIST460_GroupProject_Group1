import streamlit as st

from fetch_data import fetch_data


def validate_user_ui():
    st.header("Validate User Credentials")

    username = st.text_input("Enter Email")
    password = st.text_input("Enter Password", type="password")

    if st.button("Validate Credentials"):
        input_params = {}
        if not username.strip():
            st.error("Email is required.")
            return
        if not password.strip():
            st.error("Password is required.")
            return

        input_params["username"] = username.strip()
        input_params["password"] = password.strip()

        df = fetch_data("validate_user/", input_params)

        if df is not None and not df.empty:
            st.success("User validated successfully!")
            st.write(
                f"AppUserID: {df['AppUserID'].values[0]}, "
                f"Fullname: {df['Fullname'].values[0]}"
            )
            st.session_state.app_user_id = int(df["AppUserID"].values[0])
        else:
            st.info("Invalid email or password.")
