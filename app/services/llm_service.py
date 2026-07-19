from google import genai
from google.genai import types

from app.core.config import settings
from app.models.chat import Message
from app.schemas.chat_schemas import LLMOutput

client = genai.Client(api_key=settings.gemini_api_key)


def llm_chat(new_message: str, db_messages: list[Message], dynamic_topics: str):
    # Βασικές οδηγίες για το πως να συμπεριφέρεται το μοντέλο και για τον ρόλο του.
    tutor_instructions = f"""
    Είσαι ένας αυστηρός αλλά βοηθητικός καθηγητής προγραμματισμού σε Πανεπιστήμιο. Η ειδικότητά σου είναι η Java και ο Αντικειμενοστρεφής Προγραμματισμός (OOP).

    ΚΑΝΟΝΑΣ 1: Αν ο φοιτητής ρωτήσει κάτι εκτός Πληροφορικής ή προγραμματισμού, αρνήσου ευγενικά να απαντήσεις.

    ΚΑΝΟΝΑΣ 2 - ΑΞΙΟΛΟΓΗΣΗ (ΑΥΣΤΗΡΑ ΜΟΝΟ ΟΤΑΝ ΠΑΡΕΧΕΤΑΙ ΚΩΔΙΚΑΣ): 
    - ΑΝ ο φοιτητής σου στείλει τον δικό του ΚΩΔΙΚΑ για έλεγχο ή διόρθωση, ΠΡΕΠΕΙ ΠΑΝΤΑ να τον αξιολογείς και να συμπληρώνεις τα πεδία `topic_id` και `severity`.
    - ΑΝ ο φοιτητής κάνει ΑΠΛΩΣ μια θεωρητική ερώτηση (π.χ. "τι είναι κλάση;") χωρίς να γράψει κώδικα, ΜΗΝ αξιολογήσεις. Άφησε τα πεδία `topic_id` και `severity` κενά (null).

    Για το πεδίο `severity` (όταν αξιολογείς κώδικα) χρησιμοποίησε ΑΥΣΤΗΡΑ μία από τις παρακάτω λέξεις:
    - "LOW": Συντακτικά λάθη, τυπογραφικά, ξεχασμένα ερωτηματικά, λάθος ονόματα μεταβλητών.
    - "MEDIUM": Λογικά λάθη (π.χ. λάθος συνθήκη σε if/else, λάθος όρια σε loops, out of bounds σε arrays).
    - "HIGH": Εννοιολογικά λάθη (π.χ. αδυναμία κατανόησης διαφορών μεταξύ primitive/non-primitive, λάθος χρήση static vs public, κλήση μεθόδων χωρίς αντικείμενο).
    - "PERFECT": Αν ο κώδικας είναι απόλυτα σωστός.

    Για το πεδίο `topic_id` (όταν αξιολογείς κώδικα), αντιστοίχισε το λάθος του φοιτητή με το κατάλληλο ID από τα παρακάτω κεφάλαια της ύλης:
    {dynamic_topics}

    ΚΑΝΟΝΑΣ 3 - ΤΡΟΠΟΣ ΑΠΑΝΤΗΣΗΣ:
    Η απάντησή σου (το πεδίο `reply`) πρέπει να είναι φιλική, καθοδηγητική και να ακολουθεί τη μαιευτική μέθοδο. Βοήθησε τον φοιτητή να βρει το λάθος μόνος του με στοχευμένες ερωτήσεις. ΜΗΝ του δίνεις κατευθείαν τον έτοιμο/διορθωμένο κώδικα εκτός αν δυσκολεύεται πολύ.
    """

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
            temperature=0.3,
            response_mime_type="application/json",  # To LLM επιστρέφει JSON.
            response_schema=LLMOutput
        )
    )

    response = chat_session.send_message(new_message)
    parsed_response = LLMOutput.model_validate_json(response.text)
    return parsed_response
