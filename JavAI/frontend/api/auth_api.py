import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# API request για login
def login_user(email: str, password: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password}
        )
        if response.status_code == 200:
            return True, response.json().get("access_token")
        else:
            return False, response.json().get("detail", "Αποτυχία σύνδεσης.")
    except requests.exceptions.RequestException as e:
        return False, "Σφάλμα επικοινωνίας με τον server. Βεβαιωθείτε ότι το backend τρέχει."


# API request για register (φοιτητή)
def register_student(first_name: str, last_name: str, email: str, password: str):
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "password": password
    }
    try:
        response = requests.post(
            f"{API_BASE_URL}/users/register/student",
            json=payload
        )
        if response.status_code == 201:
            return True, "Ο λογαριασμός δημιουργήθηκε! Μπορείτε πλέον να συνδεθείτε."
        else:
            return False, response.json().get("detail", "Σφάλμα κατά την εγγραφή.")
    except requests.exceptions.RequestException as e:
        return False, "Σφάλμα επικοινωνίας με τον server. Βεβαιωθείτε ότι το backend τρέχει."
