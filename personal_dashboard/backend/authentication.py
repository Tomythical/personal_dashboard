import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def authenticate():
    with open("personal_dashboard/passwords.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Pre-hashing all plain text passwords once
    # Hasher.hash_passwords(config['credentials'])

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["pre-authorized"],
    )

    authenticator.login("main")
    if st.session_state["authentication_status"]:
        authenticator.logout("Logout", "main")
        return True
    elif st.session_state["authentication_status"] == False:
        st.error("Username/password is incorrect")
        return False
    elif st.session_state["authentication_status"] == None:
        st.warning("Please enter your username and password")
        return False
