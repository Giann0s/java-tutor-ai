import os

import streamlit as st
from dotenv import load_dotenv

from api.auth_api import login_user, register_student

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

if "access_token" not in st.session_state:
    st.session_state["access_token"] = None


def main():
    st.title("JavAI")

    if st.session_state['access_token']:
        st.success("Είστε συνδεδεμένος!")
        if st.button("Αποσύνδεση"):
            st.session_state['access_token'] = None
            st.rerun()
        return

    tab1, tab2 = st.tabs(["Σύνδεση", "Εγγραφή φοιτητή"])

    with tab1:
        st.subheader("Σύνδεση Χρήστη")
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Κωδικός", type="password", key="login_pass")

        if st.button("Είσοδος"):
            if login_email and login_password:
                with st.spinner("Επαλήθευση στοιχείων..."):
                    success, result = login_user(login_email, login_password)

                if success:
                    st.session_state['access_token'] = result
                    st.success("Επιτυχής σύνδεση!")
                    st.switch_page("pages/1_student_chat.py")
                else:
                    st.error(result)
            else:
                st.warning("Παρακαλώ συμπληρώστε όλα τα πεδία.")

    with tab2:
        st.subheader("Εγγραφή Νέου Φοιτητή")
        reg_first_name = st.text_input("Όνομα")
        reg_last_name = st.text_input("Επώνυμο")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Κωδικός", type="password", key="reg_pass")

        if st.button("Δημιουργία Λογαριασμού"):
            if reg_first_name and reg_last_name and reg_email and reg_password:
                with st.spinner("Δημιουργία λογαριασμού..."):
                    success, message = register_student(reg_first_name, reg_last_name, reg_email, reg_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Παρακαλώ συμπληρώστε όλα τα πεδία.")


if __name__ == "__main__":
    main()
