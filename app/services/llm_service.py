import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.chat import Message
from app.schemas.chat_schemas import LLMOutput
from app.schemas.exercise_schemas import CodeGeneration, MCQGeneration, ExerciseSubmission, LLMCodeGrading

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


def create_code_exercise(topic_name: str, topic_description: str) -> CodeGeneration:
    generator_instructions = f"""
    Είσαι ένας έμπειρος καθηγητής προγραμματισμού. Ο σκοπός σου είναι να δημιουργείς 
    στοχευμένες, πρακτικές ασκήσεις συγγραφής κώδικα Java για τους φοιτητές σου.
    
    Πρέπει να δημιουργήσεις μια πρωτότυπη άσκηση για το εξής κεφάλαιο:
    Όνομα Κεφαλαίου: {topic_name}
    Περιγραφή Κεφαλαίου: {topic_description}
    
    ΟΔΗΓΙΕΣ ΠΡΟΣΕΓΓΙΣΗΣ (ΜΟΡΦΗ ΑΠΑΝΤΗΣΗΣ):
    - Το πεδίο `title` πρέπει να είναι σύντομο, ελκυστικό και στα Ελληνικά (π.χ. "Σύστημα Διαχείρισης Βιβλιοθήκης").
    - Το πεδίο `description` πρέπει να περιγράφει αναλυτικά το σενάριο και τι ακριβώς πρέπει να προγραμματίσει ο φοιτητής.
    - Το πεδίο `starting_code` (αν χρειάζεται) να περιέχει τον βασικό σκελετό σε Java με σχόλια `// TODO`. Αν η άσκηση είναι πολύ απλή, μπορείς να το αφήσεις null.
    - Το πεδίο `reference_solution` πρέπει να περιέχει την πλήρη και σωστή λύση σε κώδικα Java.
    - Το πεδίο `difficulty` πρέπει να είναι ΑΥΣΤΗΡΑ μία από τις εξής λέξεις: "EASY", "MEDIUM", "HARD", ανάλογα με την πολυπλοκότητα της άσκησης που έφτιαξες.
    """

    prompt = "Φτιάξε μια νέα άσκηση συγγραφής κώδικα αποκλειστικά για αυτό το θέμα."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generator_instructions,
                temperature=0.7,  # Για να έχει περισσότερη δημιουργικότητα
                response_mime_type="application/json",
                response_schema=CodeGeneration
            )
        )

        parsed_response = CodeGeneration.model_validate_json(response.text)
        return parsed_response
    except Exception as e:
        logging.error(f"Failed to generate code task: {str(e)}")
        raise RuntimeError(f"Αποτυχία επικοινωνίας με το LLM για τη δημιουργία άσκησης.")


def create_mcq_exercise(topic_name: str, topic_description: str) -> MCQGeneration:
    generator_instructions = f"""
        Είσαι ένας έμπειρος καθηγητής προγραμματισμού σε Πανεπιστήμιο. Ο σκοπός σου είναι να 
        δημιουργείς στοχευμένες ερωτήσεις πολλαπλής επιλογής (MCQ) πάνω στη Java για τους φοιτητές σου.

        Πρέπει να δημιουργήσεις μια πρωτότυπη ερώτηση για το εξής κεφάλαιο:
        Όνομα Κεφαλαίου: {topic_name}
        Περιγραφή Κεφαλαίου: {topic_description}

        ΟΔΗΓΙΕΣ ΠΡΟΣΕΓΓΙΣΗΣ (ΜΟΡΦΗ ΑΠΑΝΤΗΣΗΣ):
        - Το `question_text` πρέπει να είναι σαφές και στα Ελληνικά. Μπορεί να περιέχει και ένα μικρό snippet κώδικα αν χρειάζεται (π.χ. "Τι θα τυπώσει ο παρακάτω κώδικας; ...").
        - Τα πεδία `option_a`, `option_b`, `option_c`, `option_d` πρέπει να περιέχουν τις 4 πιθανές απαντήσεις. Μία μόνο πρέπει να είναι 100% σωστή. Οι άλλες πρέπει να είναι αληθοφανή λάθη (distractors).
        - Το πεδίο `correct_option` πρέπει να περιέχει ΑΥΣΤΗΡΑ μόνο ένα γράμμα κεφαλαίο: "A", "B", "C" ή "D".
        - Το πεδίο `explanation` πρέπει να εξηγεί σύντομα γιατί η σωστή απάντηση είναι αυτή που είναι.
        """

    prompt = "Φτιάξε μια νέα ερώτηση πολλαπλής επιλογής αποκλειστικά για αυτό το θέμα."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generator_instructions,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=MCQGeneration,
            )
        )

        parsed_response = MCQGeneration.model_validate_json(response.text)
        return parsed_response
    except Exception as e:
        import logging
        logging.error(f"Failed to generate MCQ task: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM για τη δημιουργία άσκησης.")


def grade_code_exercise(question_content: str, student_code: str, max_points: int):
    generator_instructions = f"""
    Είσαι ένας αυστηρός αλλά δίκαιος καθηγητής Πληροφορικής στο Πανεπιστήμιο. 
    Ειδικεύεσαι στη γλώσσα προγραμματισμού Java.
    Ο ρόλος σου είναι να αξιολογείς τον κώδικα που υποβάλλουν οι φοιτητές με βάση την εκφώνηση της άσκησης.
    
    Κανόνες αξιολόγησης:
    1. Έλεγξε αν ο κώδικας λύνει το πρόβλημα που ζητείται.
    2. Έλεγξε για συντακτικά λάθη (syntax errors), λογικά λάθη (logic bugs) ή κακές πρακτικές (π.χ. off-by-one errors σε loops).
    3. Το `is_correct` πρέπει να είναι true ΜΟΝΟ αν ο κώδικας είναι πλήρως λειτουργικός και απαντά σωστά στην εκφώνηση.
    4. Το `score_awarded` πρέπει να είναι ένας αριθμός από το 0 έως το max_points. Βάλε μερικούς πόντους αν η λογική είναι σωστή αλλά υπάρχει μικρό συντακτικό λάθος.
    5. Το `llm_feedback` πρέπει να είναι γραμμένο στα Ελληνικά, με παιδαγωγικό ύφος. Εξήγησε τι πήγε στραβά, χωρίς απαραίτητα να δώσεις κατευθείαν την έτοιμη λύση. Κάνε τον φοιτητή να σκεφτεί.
    """

    prompt = f"""
    Αξιολόγησε την παρακάτω υποβολή φοιτητή.
    
    ΜΕΓΙΣΤΟΙ ΠΟΝΤΟΙ (max_points): {max_points}
    
    ΕΚΦΩΝΗΣΗ ΑΣΚΗΣΗΣ:
    {question_content}
    
    ΚΩΔΙΚΑΣ ΦΟΙΤΗΤΗ:
    ```java
    {student_code}
    ```
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generator_instructions,
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=LLMCodeGrading
            )
        )

        parsed_response = LLMCodeGrading.model_validate_json(response.text)
        return parsed_response
    except Exception as e:
        import logging
        logging.error(f"Failed to generate code grading: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM για τη διόρθωση κώδικα.")

