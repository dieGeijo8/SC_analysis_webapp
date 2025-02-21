import hmac
import streamlit as st

def check_password():
    # Returns `True` if the user had a correct password.

    def login_form():
        # Form with widgets to collect user information.
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        # Checks whether a password entered by the user is correct.
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("User not known or password incorrect")
    return False

def auth():
    if not check_password():
        st.stop()

def main():
    st.sidebar.image("img/logo.jpg", width=50)

    pg = st.navigation({"": [st.Page("Pages/Home_page.py", title="Home Page")],
                        "Explore End Points":
                            [st.Page("Pages/OffBallRuns_page.py", title="Off-Ball Runs"),
                             st.Page("Pages/Physical_page.py", title="Physical")
                             ],
                        "Reports":
                            [st.Page("Pages/Scouting_report.py", title="Winger scouting")
                             ]
                        })
    pg.run()

if __name__ == "__main__":
    auth()
    main()