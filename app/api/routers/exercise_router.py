from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status

from app.api.dependencies import db_dependency, student_dependency
from app.schemas.exercise_schemas import ExerciseResponse, ExerciseResponse, CreatedExercise, FullExerciseResponse, \
    ExerciseSubmission
from app.services.exercise_service import generate_code_exercise, generate_mcq_exercise, get_exercises, \
    get_full_exercise, submit_exercise
from app.services.student_mastery_service import calculate_mastery_exercise

router = APIRouter(
    prefix="/exercise",
    tags=["exercise"]
)


@router.post("/code", status_code=status.HTTP_201_CREATED, response_model=CreatedExercise)
async def generate_exercise(db: db_dependency, student: student_dependency, topic_id: Optional[int] = None):
    generated_exercise = generate_code_exercise(db, student.id, topic_id)
    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε topic για δημιουργία άσκησης."
        )
    return generated_exercise


@router.post("/mcq", status_code=status.HTTP_201_CREATED, response_model=CreatedExercise)
async def generate_exercise_mcq(db: db_dependency, student: student_dependency, topic_id: Optional[int] = None):
    generated_exercise = generate_mcq_exercise(db, student.id, topic_id)
    if generated_exercise is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Δεν βρέθηκε topic για δημιουργία άσκησης."
        )
    return generated_exercise


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[ExerciseResponse])
async def get_all_exercises(db: db_dependency, student: student_dependency):
    exercises = get_exercises(db, student.id)
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
