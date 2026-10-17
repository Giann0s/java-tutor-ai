import './QuestionCard.css';

export function QuestionCard({
    question, 
    index,
    userAnswer,
    onAnswerChange,
    hasSolved,
    isSubmitting,
    questionResult
}) {

    const isMcq = question.question_type === 'mcq';

    return (
        <div className="question-card">
            <div className="question-header">
                <span className="question-number">Ερώτημα {index + 1}</span>
                <div className="question-meta">
                    {question.content.difficulty && (
                        <span className="diff-badge">{question.content.difficulty}</span>
                    )}
                    <span className="points-badge">{question.points} πόντοι</span>
                </div>
            </div>

            <div className="question-prompt">
                {isMcq ? question.content.text : question.content.description}
            </div>
            
            {/* Answer area for each type of exercise */}
            {isMcq ? (
                <div className="mcq-choices">
                    {question.choices.map((choice) => {
                        const isSelected = userAnswer === String(choice.id);

                        let statusClass = "";
                        if (hasSolved) {
                            if (choice.is_correct) statusClass = "correct-choice";
                            else if (isSelected) statusClass = "wrong-choice";
                        }

                        return (
                            <button
                                key={choice.id}
                                type="button"
                                className={`choice-btn ${isSelected ? 'selected' : ''} ${statusClass}`}
                                disabled={hasSolved || isSubmitting}
                            >
                                {choice.text}
                            </button>
                        );
                    })}
                </div>
            ) : (
                <textarea
                    className="code-textarea"
                    value={userAnswer}
                    onChange={(e) => onAnswerChange(question.id, e.target.value)}
                    placeholder="// Γράψτε τον κώδικα Java έδω..."
                    disabled={hasSolved || isSubmitting}
                    rows={12}
                    spellCheck="false"
                />
            )}

            {questionResult && (
                <div className={`feedback-box ${questionResult.is_correct ? 'feedback-success' : 'feedback-error'}`}>
                    <strong>Αξιολόγηση ({questionResult.score_awarded}/{question.points} πόντοι)</strong>
                    <p>{questionResult.llm_feedback}</p>

                </div>
            )}

            {/* Solution (it's unlocked when hasSolved becomse true) */}
            {hasSolved && (
                <div className="solution-box">
                    {isMcq && question.content.explanation && (
                        <>
                            <strong>Εξήγηση:</strong>
                            <p>{question.content.explanation}</p>
                        </>
                    )}
                    {!isMcq && question.correct_answer && (
                        <>
                            <strong>Ενδεικτική Λύση:</strong>
                            <pre className="reference-code">{question.correct_answer}</pre>
                        </>
                    )}
                </div>
            )}
        </div>

    );
}