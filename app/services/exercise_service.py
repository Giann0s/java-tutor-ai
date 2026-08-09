import json
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.attempt import ExerciseAttempt, StudentAnswer
from app.models.exercise import Exercise, Question, Choice
from app.models.user import Topic, StudentMastery
from app.schemas.exercise_schemas import CreatedExercise, ExerciseSubmission
from app.services import llm_service


def get_target_topic(db: Session, user_id: int, requested_topic_id: Optional[int] = None):
    # Αν ο φοιτητής διάλεξε topic μόνος του
    if requested_topic_id:
        return db.query(Topic).filter(Topic.id == requested_topic_id).first()

    # Αν άφησε το LLM να διαλέξει topic
    weakest_mastery = db.query(StudentMastery).filter(
        StudentMastery.user_id == user_id
    ).order_by(StudentMastery.mastery_level.asc()).first()

    if weakest_mastery:
        return db.query(Topic).filter(Topic.id == weakest_mastery.topic_id).first()

    # Cold start: Αν δεν έχει καθόλου σκορ επιστρέφεται το πρώτο topic
    return db.query(Topic).first()


def generate_code_exercise(db: Session, user_id: int, topic_id: Optional[int] = None):
    target_topic = get_target_topic(db, user_id, topic_id)

    if not target_topic:
        return None

    llm_exercise_data = llm_service.create_code_exercise(target_topic.name, target_topic.description)

    new_exercise = Exercise(
        title=llm_exercise_data.title,
        keywords=target_topic.name,
        creator_id=user_id,
        created_at=datetime.now()
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    question_content_dict = {
        "description": llm_exercise_data.description,
        "starting_code": llm_exercise_data.starting_code,
        "difficulty": llm_exercise_data.difficulty
    }

    new_question = Question(
        exercise_id=new_exercise.id,
        topic_id=target_topic.id,
        question_type="code",
        content=json.dumps(question_content_dict),
        correct_answer=llm_exercise_data.reference_solution,
        points=10
    )

    db.add(new_question)
    db.commit()

    safe_data = llm_exercise_data.model_dump()
    safe_data.pop("reference_solution", None)  # αφαιρούμε την ενδεικτική λύση

    return CreatedExercise(
        exercise_id=new_exercise.id,
        topic=target_topic.name,
        type="code",
        data=safe_data
    )


def generate_mcq_exercise(db: Session, user_id: int, topic_id: Optional[int] = None):
    target_topic = get_target_topic(db, user_id, topic_id)

    if not target_topic:
        return None

    llm_mcq_data = llm_service.create_mcq_exercise(target_topic.name, target_topic.description)

    new_exercise = Exercise(
        title=f"Multiple Choice - {target_topic.name}",
        keywords=target_topic.name,
        creator_id=user_id,
        created_at=datetime.now()
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    question_content_dict = {
        "text": llm_mcq_data.question_text,
        "explanation": llm_mcq_data.explanation
    }

    new_question = Question(
        exercise_id=new_exercise.id,
        topic_id=target_topic.id,
        question_type="mcq",
        content=json.dumps(question_content_dict),
        correct_answer=None,
        points=5
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    options_mapping = {
        "A": llm_mcq_data.option_a,
        "B": llm_mcq_data.option_b,
        "C": llm_mcq_data.option_c,
        "D": llm_mcq_data.option_d
    }

    for letter, text in options_mapping.items():
        # Ελέγχουμε δυναμικά αν αυτό το γράμμα είναι η σωστή επιλογή
        is_this_choice_correct = (letter == llm_mcq_data.correct_option)

        new_choice = Choice(
            question_id=new_question.id,
            text=text,
            is_correct=is_this_choice_correct
        )
        db.add(new_choice)

    db.commit()

    safe_data = llm_mcq_data.model_dump()

    safe_data.pop("correct_option", None)
    safe_data.pop("explanation", None)

    return CreatedExercise(
        exercise_id=new_exercise.id,
        topic=target_topic.name,
        type="mcq",
        data=safe_data
    )


def get_exercises(db: Session, user_id: int):
    exercises = db.query(Exercise).filter(
        (Exercise.creator_id == user_id) | (Exercise.is_public == True)
    ).all()
    if not exercises:
        return None
    return exercises


def get_full_exercise(db: Session, exercise_id: int, user_id: int):
    exercise = db.query(Exercise).options(
        joinedload(Exercise.questions).joinedload(Question.choices)
    ).filter(
        Exercise.id == exercise_id,
        (Exercise.creator_id == user_id) | (Exercise.is_public == True)
    ).first()

    if not exercise:
        return None

    # Έλεγχος για το αν ο φοιτητής έχει λύσει την άσκηση
    attempt = db.query(ExerciseAttempt).filter(
        ExerciseAttempt.exercise_id == exercise_id,
        ExerciseAttempt.user_id == user_id
    ).first()

    has_solved = attempt is not None

    questions_out = []
    for q in exercise.questions:
        content_dict = json.loads(q.content) if q.content else {}

        if not has_solved and "explanation" in content_dict:
            content_dict.pop("explanation", None)

        choices_out = []
        for c in q.choices:
            choices_out.append({
                "id": c.id,
                "text": c.text,
                "is_correct": c.is_correct if has_solved else None
            })

        questions_out.append({
            "id": q.id,
            "question_type": q.question_type,
            "content": content_dict,
            "points": q.points,
            "correct_answer": q.correct_answer if has_solved else None,
            "choices": choices_out
        })

    return {
        "id": exercise.id,
        "title": exercise.title,
        "keywords": exercise.keywords,
        "has_solved": has_solved,
        "questions": questions_out
    }


def submit_exercise(db: Session, exercise_id: int, user_id: int, submission: ExerciseSubmission):
    existing_attempt = db.query(ExerciseAttempt).filter(
        ExerciseAttempt.exercise_id == exercise_id,
        ExerciseAttempt.user_id == user_id
    ).first()

    if existing_attempt:
        return False

    new_attempt = ExerciseAttempt(
        user_id=user_id,
        exercise_id=exercise_id,
        status="completed",
        completed_at=datetime.now(),
        total_score=0.0
    )
    db.add(new_attempt)
    db.flush()  # Απαραίτητο για να πάρουμε το νέο new_attempt.id

    total_earned_score = 0.0

    for ans in submission.answers:
        question = db.query(Question).filter(
            Question.id == ans.question_id,
            Question.exercise_id == exercise_id
        ).first()

        if not question:
            continue

        is_correct = False
        score_awarded = 0.0
        llm_feedback = None

        if question.question_type == "mcq":
            selected_choice = db.query(Choice).filter(Choice.id == int(ans.provided_answer)).first()

            if selected_choice and selected_choice.is_correct:
                is_correct = True
                score_awarded = float(question.points)
                llm_feedback = "Σωστή απάντηση!"
            else:
                llm_feedback = "Λάθος επιλογή."

        elif question.question_type == "code":
            code_grading = llm_service.grade_code_exercise(question.content, ans.provided_answer, question.points)
            is_correct = code_grading.is_correct
            score_awarded = code_grading.score_awarded
            llm_feedback = code_grading.llm_feedback

        student_answer = StudentAnswer(
            attempt_id=new_attempt.id,
            question_id=question.id,
            provided_answer=ans.provided_answer,
            is_correct=is_correct,
            llm_feedback=llm_feedback,
            score_awarded=score_awarded
        )
        db.add(student_answer)
        total_earned_score += score_awarded

    new_attempt.total_score = total_earned_score
    db.commit()
    db.refresh(new_attempt)

    return new_attempt
