import logging

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.chat import Message
from app.schemas.chat_schemas import LLMOutput
from app.schemas.exercise_schemas import CodeGeneration, MCQGeneration, ExerciseSubmission, LLMCodeGrading, \
    ProfessorMCQTest, ProfessorCodeTest

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

    try:
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
    except Exception as e:
        import logging
        logging.error(f"Failed to contact LLM: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM.")

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


def create_mcq_exercise(topic_name: str, topic_description: str):
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


def llm_chat_professor(new_message: str, db_messages: list[Message]):
    instructions = f"""
    Είσαι ένας εξαιρετικά καταρτισμένος βοηθός (AI Assistant) και σύμβουλος για έναν Καθηγητή Πληροφορικής Πανεπιστημιακού επιπέδου, με ειδίκευση στη Java και τον Προγραμματισμό.
    Ο συνομιλητής σου ΔΕΝ είναι φοιτητής, αλλά ο ΙΔΙΟΣ Ο ΚΑΘΗΓΗΤΗΣ.
    
    ΣΚΟΠΟΣ ΣΟΥ:
    Να τον βοηθάς στον σχεδιασμό μαθημάτων, στη δημιουργία εκπαιδευτικού υλικού, στην εύρεση ιδεών για απαιτητικές εργασίες/projects, στη συγγραφή και βελτιστοποίηση πολύπλοκου κώδικα, και στον σχεδιασμό διαγωνισμάτων.
    
    ΤΟΝΟΣ ΚΑΙ ΥΦΟΣ:
    Επαγγελματικό, συναδελφικό, άμεσο και απολύτως τεχνικά ακριβές. Απευθύνεσαι σε έναν ειδικό του χώρου, οπότε μην υπεραπλουστεύεις τις έννοιες και χρησιμοποίησε ορθή ακαδημαϊκή και τεχνολογική ορολογία.
    
    ΚΑΝΟΝΕΣ ΕΞΟΔΟΥ (JSON SCHEMA):
    Το σύστημα περιμένει υποχρεωτικά την απάντησή σου σε μορφή JSON με βάση το προκαθορισμένο schema (reply, topic_id, severity).
    - Στο πεδίο `reply`: Γράψε την αναλυτική απάντησή σου προς τον καθηγητή.
    - Τα πεδία `topic_id` και `severity`: ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ ΠΑΝΤΑ null. Αυτά τα πεδία χρησιμοποιούνται μόνο στο σύστημα των φοιτητών και δεν έχουν καμία χρησιμότητα εδώ.
    """

    gemini_history = []
    for msg in db_messages:
        gemini_history.append(
            types.Content(
                role=msg.sender_role,
                parts=[types.Part.from_text(text=msg.content)]
            )
        )

    try:
        chat_session = client.chats.create(
            model='gemini-2.5-flash',
            history=gemini_history,
            config=types.GenerateContentConfig(
                system_instruction=instructions,
                temperature=0.3,
                response_mime_type='application/json',
                response_schema=LLMOutput
            )
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to contact LLM: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM.")
    response = chat_session.send_message(new_message)
    parsed_response = LLMOutput.model_validate_json(response.text)
    return parsed_response


def create_professor_mcq_test(keywords: str, dynamic_topics: str, num_questions: int = 5):
    generator_instructions = f"""
    Είσαι ένας έμπειρος καθηγητής Πανεπιστημίου με ειδίκευση στην Πληροφορική και τον προγραμματισμό (Java). 
    Ο σκοπός σου είναι να δημιουργήσεις ένα απαιτητικό, ακαδημαϊκού επιπέδου τεστ πολλαπλής επιλογής.

    ΛΕΞΕΙΣ ΚΛΕΙΔΙΑ (KEYWORDS) ΑΞΙΟΛΟΓΗΣΗΣ: {keywords}

    ΑΥΣΤΗΡΟΙ ΚΑΝΟΝΕΣ ΔΗΜΙΟΥΡΓΙΑΣ:
    1. Δομή & Πλήθος: Δημιούργησε ΑΚΡΙΒΩΣ {num_questions} ερωτήσεις. Κάθε ερώτηση πρέπει να εξετάζει μια διαφορετική, στοχευμένη πτυχή από τα Keywords.
    2. Μοναδική Ορθότητα: Μόνο μία είναι η σωστή απάντηση στο καθένα. Φρόντισε οι υπόλοιπες τρεις επιλογές (distractors) να είναι αληθοφανείς, αλλά τεχνικά λανθασμένες.
    3. Πλήρης Εκφώνηση (Σημαντικό!): Το πεδίο `text` πρέπει να είναι αυθύπαρκτο. Αν η ερώτηση βασίζεται σε απόσπασμα κώδικα, ο κώδικας ΠΡΕΠΕΙ να ενσωματωθεί μέσα στο `text` (χρησιμοποίησε \n για αλλαγές γραμμής, π.χ. "Δίνεται ο κώδικας:\nint x = 5;\n...").
    4. Αυστηρό Format Απάντησης: Το πεδίο `correct_option` ΠΡΕΠΕΙ να περιέχει ΑΥΣΤΗΡΑ και ΜΟΝΟ ένα αγγλικό κεφαλαίο γράμμα: A, B, C, ή D. Απαγορεύεται οποιαδήποτε άλλη λέξη ή επεξήγηση σε αυτό το πεδίο.
    5. Αντιστοίχιση Ύλης: Για κάθε ερώτηση, διάλεξε το πιο κατάλληλο 'topic_id' από την παρακάτω διαθέσιμη ύλη.

    ΔΙΑΘΕΣΙΜΑ TOPICS:
    {dynamic_topics}
    """

    prompt = f"Φτιάξε το τεστ πολλαπλής επιλογής βασισμένο στα keywords: '{keywords}'."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generator_instructions,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=ProfessorMCQTest,
            )
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to generate Professor MCQ Test: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM για τη δημιουργία της άσκησης πολλαπλής.")

    return ProfessorMCQTest.model_validate_json(response.text)


def create_professor_code_test(keywords: str, dynamic_topics: str, num_questions: int):
    generator_instructions = f"""
    Είσαι ένας έμπειρος καθηγητής Πανεπιστημίου με ειδίκευση στη Java και τον Αντικειμενοστρεφή Προγραμματισμό.
    Ο σκοπός σου είναι να δημιουργήσεις ένα απαιτητικό, ακαδημαϊκού επιπέδου διαγώνισμα/εργασία ανάπτυξης κώδικα για τους φοιτητές σου.
    
    ΛΕΞΕΙΣ ΚΛΕΙΔΙΑ (KEYWORDS) ΑΞΙΟΛΟΓΗΣΗΣ: 
    {keywords}
    
    ΑΥΣΤΗΡΟΙ ΚΑΝΟΝΕΣ ΔΗΜΙΟΥΡΓΙΑΣ:
    1. Πλήθος Ερωτημάτων: Δημιούργησε ΑΚΡΙΒΩΣ {num_questions} ξεχωριστά ερωτήματα ανάπτυξης κώδικα.
    2. Ποικιλία: Κάθε ερώτημα πρέπει να εξετάζει μια διαφορετική, στοχευμένη πτυχή από τα Keywords.
    3. Αντιστοίχιση Ύλης: Για κάθε ερώτημα, ΠΡΕΠΕΙ να διαλέξεις το πιο κατάλληλο 'topic_id' από την παρακάτω διαθέσιμη ύλη:
        
    ΔΙΑΘΕΣΙΜΑ TOPICS:
    {dynamic_topics}
    
    ΟΔΗΓΙΕΣ ΠΕΡΙΕΧΟΜΕΝΟΥ (Για κάθε ερώτημα):
    - `description`: Πρέπει να περιγράφει αναλυτικά, βήμα-προς-βήμα και με σαφήνεια το πρόβλημα στα Ελληνικά.
    - `starting_code` (ΚΡΙΣΙΜΟ): Πρέπει να περιέχει ΜΟΝΟ τον βασικό σκελετό (ονόματα κλάσεων, υπογραφές μεθόδων). ΑΠΑΓΟΡΕΥΕΤΑΙ ΑΥΣΤΗΡΑ να συμπεριλάβεις την υλοποίηση, τη λογική ή τον κώδικα της λύσης σε αυτό το πεδίο. Το σώμα των μεθόδων πρέπει να είναι άδειο. 
    Χρησιμοποίησε μόνο σχόλια της μορφής `// TODO: [Οδηγία]` για να καθοδηγήσεις τον φοιτητή στο τι πρέπει να γράψει. Επίσης δεν είναι υποχρεωτικό πεδίο.
    - `reference_solution`: Ο πλήρης, λειτουργικός και βέλτιστος κώδικας Java που λύνει το πρόβλημα. Πρέπει να ταιριάζει απόλυτα με τον σκελετό που άφησες στο `starting_code`.
    - `difficulty`: Πρέπει να είναι αυστηρά μία από τις τιμές: "EASY", "MEDIUM", "HARD".
    - `points`: Δώσε μια λογική βαθμολογία (π.χ. 10, 15, ή 20) ανάλογα με τη δυσκολία του ερωτήματος.
    """

    prompt = f"Φτιάξε ένα διαγώνισμα κώδικα βασισμένο στα keywords: '{keywords}'."

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=generator_instructions,
                temperature=0.7,  # 0.7 για να υπάρχει ποικιλία στα σενάρια των ασκήσεων
                response_mime_type="application/json",
                # ΠΡΟΣΟΧΗ: Χρησιμοποιούμε το νέο schema εδώ!
                response_schema=ProfessorCodeTest
            )
        )
    except Exception as e:
        import logging
        logging.error(f"Failed to generate Professor Code Test: {str(e)}")
        raise RuntimeError("Αποτυχία επικοινωνίας με το LLM για τη δημιουργία της άσκησης κώδικα.")

    return ProfessorCodeTest.model_validate_json(response.text)