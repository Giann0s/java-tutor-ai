import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


# API request για chat φοιτητή
def send_chat_message(token: str, conversation_id: int, user_text: str):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "conversation_id": conversation_id,
        "user_text": user_text
    }

    try:
        response = requests.post(f"{API_BASE_URL}/chat/", json=payload, headers=headers)
        if response.status_code == 201:
            return True, response.json()
        return False, response.json().get("detail", "Σφάλμα κατά την αποστολή.")
    except requests.exceptions.RequestException:
        return False, "Σφάλμα επικοινωνίας με τον server."


# API request για ανάκτηση συζητήσεων
def get_user_conversations(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/chat/", headers=headers)
        if response.status_code == 200:
            return True, response.json()
        return False, "Αποτυχία ανάκτησης ιστορικού."
    except requests.exceptions.RequestException:
        return False, "Σφάλμα επικοινωνίας με τον server."


# API request για διαγραφή συζήτησης
def delete_conversation(token: str, conversation_id: int):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.delete(f"{API_BASE_URL}/chat/{conversation_id}", headers=headers)
        if response.status_code == 204:
            return True, "Η συζήτηση διαγράφηκε."
        return False, "Αποτυχία διαγραφής."
    except requests.exceptions.RequestException:
        return False, "Σφάλμα επικοινωνίας με τον server."
