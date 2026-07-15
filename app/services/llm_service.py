from google import genai
from google.genai import types

from app.core.config import settings
from app.models.chat import Message

client = genai.Client(api_key=settings.gemini_api_key)


def llm_chat(new_message: str, db_messages: list[Message]) -> str:
    # Βασικές οδηγίες για το πως να συμπεριφέρεται το μοντέλο και για τον ρόλο του.
    tutor_instructions = (
        "Είσαι ένας αυστηρός αλλά βοηθητικός καθηγητής προγραμματισμού σε Πανεπιστήμιο. "
        "Η ειδικότητά σου είναι η γλώσσα Java, ο Αντικειμενοστρεφής Προγραμματισμός (OOP),"
        "η κληρονομικότητα, ο Πολυμορφισμός."
        "Ο κανόνας σου είναι ένας: Αν ο φοιτητής σε ρωτήσει οτιδήποτε δεν έχει σχέση με τη Java "
        "ή την επιστήμη της Πληροφορικής, ΠΡΕΠΕΙ να αρνηθείς ευγενικά να απαντήσεις "
        "και να του υπενθυμίσεις ότι είσαι εδώ μόνο για θέματα προγραμματισμού."
    )

    # Ιστορικό μηνυμάτων της συζήτησης
    gemini_history = []
    for msg in db_messages:
        gemini_history.append(
            types.Content(
                role=msg.sender_role,
                parts=[types.Part.from_text(text=msg.content)]  # Περιμένει κείμενο
            )
        )

    # Δημιουργία ενός chat_session ώστε το μοντέλο να αποκτήσει μνήμη
    chat_session = client.chats.create(
        model='gemini-2.5-flash',
        history=gemini_history,
        config=types.GenerateContentConfig(
            system_instruction=tutor_instructions,
            temperature=0.3
        )
    )

    response = chat_session.send_message(new_message)
    return response.text
