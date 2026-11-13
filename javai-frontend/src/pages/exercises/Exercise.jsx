import './Exercise.css';
import { useContext, useEffect, useState, useCallback } from 'react';
import api from '../../api/axiosConfig';
import AuthContext from '../../context/AuthContext';
import { Sidebar } from '../../components/Sidebar';
import { NewExerciseModal } from '../../components/NewExerciseModal';
import { QuestionCard } from '../../components/QuestionCard';
import { formatJavaCode } from '../../utils/formatters';
import { TopicsModal } from '../../components/TopicsModal';

export function Exercise() {
    const { token, isProfessor } = useContext(AuthContext);

    // States for the modal and sidebar
    const [exercises, setExercises] = useState([]);
    const [topics, setTopics] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isTopicModalOpen, setIsTopicModalOpen] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);

    // States for the currect exercise
    const [currentExerciseId, setCurrentExerciseId] = useState(null);
    const [currentExercise, setCurrentExercise] = useState(null);

    // States for the answers of the student
    const [userAnswers, setUserAnswers] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submissionResult, setSubmissionResult] = useState(null);

    // Fetch exercise history and topics
    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const topicRes = await api.get('/topics/');
                setTopics(topicRes.data);
            } catch (error) {
                console.error("Σφάλμα στη φόρτωση των topics: ", error);
            }

            try {
                const exerciseRes = await api.get('/exercise/');
                setExercises(exerciseRes.data);
            } catch (error) {
                console.error("Σφάλμα στη φόρτωση των ασκήσεων: ", error);
            }
        };

        if (token) {
            fetchInitialData();
        }
    }, [token]);

    // Fetch details of a specific exercise
    const fetchExerciseDetails = useCallback(async (exercise_id) => {
        try {
            const endpoint = isProfessor ? `/exercise/professor/${exercise_id}` : `/exercise/${exercise_id}`;

            const response = await api.get(endpoint);
            const data = response.data;
            setCurrentExercise(data);

            if (!isProfessor && !data.has_solved) {
                const initialAnswers = {};
                data.questions.forEach((q) => {
                    initialAnswers[q.id] = formatJavaCode(q.content.starting_code) || "";
                })
                setUserAnswers(initialAnswers);
            }
        } catch (error) {
            console.error("Σφάλμα στην φόρτωση της άσκησης: ", error);
        }
    }, [isProfessor])

    useEffect(() => {
        if (currentExerciseId !== null) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setSubmissionResult(null);
            fetchExerciseDetails(currentExerciseId);
        }

    }, [currentExerciseId, fetchExerciseDetails]);

    // New exercise
    const handleGenerateExercise = async (type, data) => {
        setIsGenerating(true);
        try {
            let response;
            if (isProfessor) {
                const endpoint = type === 'code' ? '/exercise/code/test' : '/exercise/test';
                response = await api.post(endpoint, data);
            } else {
                const endpoint = type === 'code' ? '/exercise/code' : '/exercise/mcq';
                const config = data ? { params: { topic_id: data } } : {}
                response = await api.post(endpoint, null, config);
            }

            const updatedList = await api.get('/exercise/');
            setExercises(updatedList.data);

            setCurrentExerciseId(response.data.exercise_id);
            setIsModalOpen(false);
        } catch (error) {
            console.error("Σφάλμα κατά την δημιουργία άσκησης: ", error);
            alert("Παρουσιάστηκε σφάλμα κατά την δημιουργία της άσκησης.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleAnswerChange = (questionId, value) => {
        setUserAnswers((prev) => ({
            ...prev,
            [questionId]: String(value)
        }));
    };

    // Submit exercise
    const handleSubmitExercise = async () => {
        if (!currentExercise || isSubmitting) return;

        const unanswered = currentExercise.questions.some(
            (q) => !userAnswers[q.id] || userAnswers[q.id].trim() === ""
        );
        if (unanswered) {
            alert("Παρακαλώ απαντήστε σε όλα τα ερωτήματα πριν την υποβολή.")
            return;
        }

        setIsSubmitting(true);
        try {
            const payload = {
                answers: currentExercise.questions.map((q) => ({
                    question_id: q.id,
                    provided_answer: userAnswers[q.id]
                }))
            };

            const response = await api.post(`/exercise/${currentExercise.id}/submit`, payload);
            setSubmissionResult(response.data);

            await fetchExerciseDetails(currentExercise.id);
        } catch (error) {
            console.error("Σφάλμα κατά την υποβολή: ", error);
            alert(error.response?.data?.detail || "Σφάλμα κατά την υποβολή της άσκησης.");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!token) return null;


    return (
        <div className="home-layout">
            <Sidebar
                mode="exercises"
                items={exercises}
                currentId={currentExerciseId}
                setCurrentId={setCurrentExerciseId}
                handleNewAction={() => setIsModalOpen(true)}
                handleNewTopic={() => setIsTopicModalOpen(true)}
            />

            <main className="main-exercise-area">
                {!currentExercise ? (
                    <div className="empty-exercise-state">
                        <h2>Επιλέξτε μια άσκηση από το ιστορικό ή δημιουργήστε μια νέα!</h2>
                    </div>
                ) : (
                    <div className="exercise-container">
                        <div className="exercise-header">
                            <div>
                                <h1>{currentExercise.title}</h1>
                                {currentExercise.keywords && (
                                    <span className="topic-badge">#{currentExercise.keywords}</span>
                                )}
                            </div>
                            {!isProfessor && currentExercise.has_solved && (
                                <span className="solved-badge">Ολοκληρωμένη</span>
                            )}
                        </div>

                        {submissionResult && (
                            <div className="score-banner">
                                <strong>{submissionResult.message}</strong> — Βαθμολογία: {submissionResult.total_score}
                            </div>
                        )}

                        <div className="questions-list">
                            {currentExercise.questions.map((q, index) => {
                                const qResult = submissionResult?.results?.find((r) => r.question_id === q.id);

                                return (
                                    <QuestionCard
                                        key={q.id}
                                        question={q}
                                        index={index}
                                        userAnswer={userAnswers[q.id] || ""}
                                        onAnswerChange={handleAnswerChange}
                                        hasSolved={isProfessor || currentExercise.has_solved}
                                        isSubmitting={isSubmitting}
                                        questionResult={qResult}
                                        isProfessor={isProfessor}
                                    />
                                );
                            })}
                        </div>

                        {!isProfessor && !currentExercise.has_solved && (
                            <div className="submit-section">
                                <button
                                    className="submit-exercise-btn"
                                    onClick={handleSubmitExercise}
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? 'Αξιολόγηση...' : 'Υποβολή Απάντησης'}
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </main>

            <NewExerciseModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                topics={topics}
                onGenerate={handleGenerateExercise}
                isGenerating={isGenerating}
                isProfessor={isProfessor}
            />

            {isProfessor && (
                <TopicsModal
                    isOpen={isTopicModalOpen}
                    onClose={() => setIsTopicModalOpen(false)}
                    topics={topics}
                    setTopics={setTopics}
                />
            )}
        </div>
    );
}