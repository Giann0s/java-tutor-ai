from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

from app.api.dependencies import db_dependency, student_dependency, professor_dependency, user_dependency
from app.schemas.exercise_schemas import ExerciseResponse, CreatedExercise, FullExerciseResponse, \
    ExerciseSubmission, GenerateProfessorTest
from app.services.exercise_service import generate_code_exercise, generate_mcq_exercise, get_exercises, \
    get_full_exercise, submit_exercise, generate_official_mcq_test, generate_official_code_test
from app.services.student_mastery_service import calculate_mastery_exercise

router = APIRouter(
    prefix="/exercise",
    tags=["exercise"]
)


@router.post("/code", status_code=status.HTTP_201_CREATED, response_model=CreatedExercise)
async def generate_exercise(db: db_dependency, student: student_dependency, topic_id: Optional[int] = None):
    try:
        generated_exercise = generate_code_exercise(db, student.id, topic_id)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε topic για δημιουργία άσκησης."
        )
    return generated_exercise


@router.post("/mcq", status_code=status.HTTP_201_CREATED, response_model=CreatedExercise)
async def generate_exercise_mcq(db: db_dependency, student: student_dependency, topic_id: Optional[int] = None):
    try:
        generated_exercise = generate_mcq_exercise(db, student.id, topic_id)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε topic για δημιουργία άσκησης."
        )
    return generated_exercise


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ExerciseResponse])
async def get_all_exercises(db: db_dependency, user: user_dependency):
    exercises = get_exercises(db, user.id)
    if exercises is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκαν ασκήσεις."
        )
    return exercises


@router.get("/{exercise_id}", status_code=status.HTTP_200_OK, response_model=FullExerciseResponse)
async def get_exercise_details(db: db_dependency, student: student_dependency, exercise_id: int):
    exercise_data = get_full_exercise(db, exercise_id, student.id)
    if not exercise_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Η άσκηση δεν βρέθηκε."
        )

    return exercise_data


@router.post("/{exercise_id}/submit", status_code=status.HTTP_200_OK)
async def submit_exercise_endpoint(
        exercise_id: int,
        submission: ExerciseSubmission,
        db: db_dependency,
        student: student_dependency,
        background_tasks: BackgroundTasks
):
    try:
        attempt = submit_exercise(db, exercise_id, student.id, submission)
    except RuntimeError as e:
        # Έλεγχος του σφάλματος αν το LLM δεν ανταποκρίνεται
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Έχετε ήδη υποβάλει αυτή την άσκηση. Δεν επιτρέπονται πολλαπλές υποβολές."
        )
    # Χρήση background tasks για να μην καθυστερεί η εμφάνιση του αποτελέσματος
    # λόγω του υπολογισμού του mastery
    background_tasks.add_task(calculate_mastery_exercise, db, attempt.id)

    results_out = []
    for answer in attempt.student_answers:
        results_out.append({
            "question_id": answer.question_id,
            "is_correct": answer.is_correct,
            "score_awarded": answer.score_awarded,
            "llm_feedback": answer.llm_feedback
        })

    return {
        "message": "Η άσκηση υποβλήθηκε επιτυχώς!",
        "total_score": attempt.total_score,
        "results": results_out
    }


@router.post("/test", status_code=status.HTTP_201_CREATED)
async def generate_official_mcq_exercise(db: db_dependency,
                                         professor: professor_dependency,
                                         exercise_request: GenerateProfessorTest):
    try:
        generated_exercise = generate_official_mcq_test(db, professor.id, exercise_request.keywords,
                                                        exercise_request.num_questions)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Αδυναμία δημιουργίας άσκησης."
        )

    return {
        "message": "Το επίσημο τεστ δημιουργήθηκε επιτυχώς και είναι πλέον ορατό στους φοιτητές!",
        "exercise_id": generated_exercise.id
    }


@router.post("/code/test", status_code=status.HTTP_201_CREATED)
async def generate_official_code_exercise(db: db_dependency,
                                          professor: professor_dependency,
                                          exercise_request: GenerateProfessorTest):
    try:
        generated_exercise = generate_official_code_test(db, professor.id, exercise_request.keywords,
                                                         exercise_request.num_questions)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )

    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Αδυναμία δημιουργίας άσκησης."
        )

    return {
        "message": "Το επίσημο τεστ δημιουργήθηκε επιτυχώς και είναι πλέον ορατό στους φοιτητές!",
        "exercise_id": generated_exercise.id
    }


@router.get("/professor/{exercise_id}", status_code=status.HTTP_200_OK, response_model=FullExerciseResponse)
async def get_professor_exercise_details(db: db_dependency, professor: professor_dependency, exercise_id: int):
    exercise_data = get_full_exercise(db, exercise_id, professor.id, is_professor=True)
    if not exercise_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Η άσκηση δεν βρέθηκε."
        )
    return exercise_data
