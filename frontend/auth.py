import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"


def is_logged_in() -> bool:
    return "access_token" in st.session_state and st.session_state["access_token"]


def get_auth_headers() -> dict:
    """Use this in every protected API call."""
    return {
        "Authorization": f"Bearer {st.session_state['access_token']}"
    }


def logout():
    for key in ["access_token", "role", "name"]:
        if key in st.session_state:
            del st.session_state[key]


def require_login():
    """
    Call this at the very top of a protected page.
    Shows a login/signup form and stops the page from
    rendering further if the user isn't logged in.
    """

    if is_logged_in():
        # Show a small logged-in status + logout button in the sidebar
        with st.sidebar:
            st.success(f"Logged in as {st.session_state.get('name', '')}")
            st.caption(f"Role: {st.session_state.get('role', '')}")
            if st.button("🚪 Logout"):
                logout()
                st.rerun()
        return  # user is logged in, let the page continue

    # -----------------------------
    # Not logged in — show login/signup
    # -----------------------------
    st.title("🔐 HireSense AI")
    st.subheader("Login or Create an Account")

    tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

    # ---------- LOGIN ----------
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input(
                "Password", type="password", key="login_password"
            )
            submitted = st.form_submit_button("Login")

            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    response = requests.post(
                        f"{BACKEND_URL}/auth/login",
                        json={"email": email, "password": password}
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["role"] = data["role"]
                        st.session_state["name"] = data["name"]
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error(
                            response.json().get("detail", "Login failed.")
                        )

    # ---------- SIGNUP ----------
    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Full Name", key="signup_name")
            email = st.text_input("Email", key="signup_email")
            password = st.text_input(
                "Password", type="password", key="signup_password"
            )
            role = st.selectbox("I am a...", ["student", "recruiter"])
            submitted = st.form_submit_button("Create Account")

            if submitted:
                if not name or not email or not password:
                    st.error("Please fill in all fields.")
                else:
                    response = requests.post(
                        f"{BACKEND_URL}/auth/signup",
                        json={
                            "name": name,
                            "email": email,
                            "password": password,
                            "role": role
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["role"] = data["role"]
                        st.session_state["name"] = data["name"]
                        st.success("Account created! You're now logged in.")
                        st.rerun()
                    else:
                        st.error(
                            response.json().get("detail", "Signup failed.")
                        )

    st.stop()
