from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field


class MCQGeneration(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: str


# class LLMChoice(BaseModel):
#     text: str = Field(description="Το κείμενο της επιλογής")
#     is_correct: bool = Field(description="True αν είναι η σωστή απάντηση, False αν είναι λάθος")
#
#
# class LLMMCQQuestion(BaseModel):
#     content: str = Field(description="Η εκφώνηση της ερώτησης")
#     explanation: str = Field(
#         description="Εξήγηση γιατί αυτή η απάντηση είναι η σωστή. Αυτό θα κρύβεται από τον φοιτητή μέχρι να απαντήσει.")
#     points: float = Field(description="Οι πόντοι που δίνει αυτή η ερώτηση")
#     choices: List[LLMChoice] = Field(description="Λίστα με 4 επιλογές (ακριβώς 1 πρέπει να είναι σωστή)")
#
#
# class LLMMCQExercise(BaseModel):
#     questions: List[LLMMCQQuestion] = Field(description="Λίστα με τις ερωτήσεις του τεστ")


class CodeGeneration(BaseModel):
    title: str
    description: str
    starting_code: Optional[str]
    reference_solution: str
    difficulty: str


class CreatedExercise(BaseModel):
    exercise_id: int
    topic: str
    type: str
    data: dict


class ExerciseResponse(BaseModel):
    id: int
    title: str
    keywords: str
    created_at: datetime
    is_public: bool

    model_config = ConfigDict(from_attributes=True)


class ChoiceDetail(BaseModel):
    id: int
    text: str
    is_correct: Optional[bool] = None


class QuestionDetail(BaseModel):
    id: int
    question_type: str
    content: dict
    points: int
    correct_answer: Optional[str] = None
    choices: List[ChoiceDetail] = []


class FullExerciseResponse(BaseModel):
    id: int
    title: str
    keywords: Optional[str]
    has_solved: bool
    questions: List[QuestionDetail]


class AnswerSubmission(BaseModel):
    question_id: int
    provided_answer: str


class ExerciseSubmission(BaseModel):
    answers: List[AnswerSubmission]


class LLMCodeGrading(BaseModel):
    is_correct: bool
    score_awarded: float
    llm_feedback: str


# Schemas για τα τεστ πολλαπλής που κάνει generate ο καθηγητής
class ProfessorMCQItem(BaseModel):
    topic_id: int = Field(description="Το ID του topic που ταιριάζει καλύτερα σε αυτή την ερώτηση")
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    explanation: str


class ProfessorMCQTest(BaseModel):
    title: str = Field(description="Ένας γενικός τίτλος για όλο το τεστ")
    questions: List[ProfessorMCQItem]


# Schemas για τα τεστ ανάπτυξης κώδικα που κάνει generate ο καθηγητής
class ProfessorCodeItem(BaseModel):
    topic_id: int = Field(description="Το ID του topic που ταιριάζει καλύτερα σε αυτό το ζητούμενο")
    description: str = Field(description="Η εκφώνηση - τι πρέπει να προγραμματίσει ο φοιτητής")
    starting_code: Optional[str] = Field(description="Βασικός σκελετός κώδικα (προαιρετικό)")
    reference_solution: str = Field(description="Η πρότυπη λύση σε Java")
    difficulty: str = Field(description="EASY, MEDIUM, ή HARD")
    points: int = Field(description="Οι πόντοι για αυτό το ερώτημα (π.χ. 10 ή 20)")


class ProfessorCodeTest(BaseModel):
    title: str = Field(description="Ο τίτλος του συνολικού διαγωνίσματος")
    questions: List[ProfessorCodeItem]


class GenerateProfessorTest(BaseModel):
    num_questions: int
    keywords: str
