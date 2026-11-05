import './NewExerciseModal.css';
import { useState } from 'react';

export function NewExerciseModal({ isOpen, onClose, topics, onGenerate, isGenerating, isProfessor = false }) {
    const [exerciseType, setExerciseType] = useState('mcq');
    const [selectedTopicId, setSelectedTopicId] = useState('');
    const [keywords, setKeywords] = useState(''); //for the professor
    const [numQuestions, setNumQuestions] = useState(5);

    if (!isOpen) return null;

    //Get the topic object in order to get the description
    const selectedTopic = topics.find((t) => t.id === Number(selectedTopicId));

    const handleSubmit = (e) => {
        e.preventDefault();
        if (isProfessor) {
            if (!keywords.trim()) {
                alert("Παρακαλώ εισάγετε λέξεις-κλειδιά για το τεστ.");
                return;
            }
            onGenerate(exerciseType, {
                keywords: keywords.trim(),
                num_questions: Number(numQuestions)
            });
        } else {
            const topicToSend = selectedTopic ? Number(selectedTopicId) : null;
            onGenerate(exerciseType, topicToSend);
        }
    };

    return (
        <div className="modal-overlay" onClick={!isGenerating ? onClose : undefined}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>{isProfessor ? 'Δημιουργία Επίσημου Τεστ' : 'Δημιουργία Νέας Άσκησης'}</h2>
                    <button
                        className="modal-close-btn"
                        onClick={onClose}
                        disabled={isGenerating}
                    >
                        &#10005;
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    <div className="form-group">
                        <label>Τύπος Άσκησης</label>
                        <div className="type-selector">
                            <button
                                type="button"
                                className={`type-card ${exerciseType === 'mcq' ? 'active' : ''}`}
                                onClick={() => setExerciseType('mcq')}
                                disabled={isGenerating}
                            >
                                <span className="type-title">Πολλαπλής Επιλογής</span>
                                <span className="type-desc">Ερώτηση θεωρίας/κώδικα</span>
                            </button>

                            <button
                                type="button"
                                className={`type-card ${exerciseType === 'code' ? 'active' : ''}`}
                                onClick={() => setExerciseType('code')}
                                disabled={isGenerating}
                            >
                                <span className="type-title">Ανάπτυξη Κώδικα</span>
                                <span className="type-desc">Συγγραφή κώδικα Java</span>
                            </button>
                        </div>

                        {isProfessor ? (
                            <>
                                <div className="form-group">
                                    <label htmlFor="keywords-input">Λέξεις-Κλειδιά</label>
                                    <input
                                        id="keywords-input"
                                        type="text"
                                        className="topic-select"
                                        placeholder="π.χ. Loops, Switch, Arrays"
                                        value={keywords}
                                        onChange={(e) => setKeywords(e.target.value)}
                                        disabled={isGenerating}
                                        required
                                    />
                                    <p className="topic-description">
                                        Το AI θα δημιουργήσει ερωτήσεις βασισμένες σε αυτές τις έννοιες και θα τις δημοσιεύσει σε όλους τους φοιτητές.
                                    </p>
                                </div>

                                <div className="form-group">
                                    <label htmlFor="num-questions-input">Πλήθος Ερωτημάτων (1 - 10)</label>
                                    <input
                                        id="num-questions-input"
                                        type="number"
                                        min={1}
                                        max={10}
                                        className="topic-select"
                                        value={numQuestions}
                                        onChange={(e) => setNumQuestions(e.target.value)}
                                        disabled={isGenerating}
                                        required
                                    />
                                </div>
                            </>
                        ) : (
                            <div className="form-group">
                                <label htmlFor="topic-select">Ενότητα (Προαιρετικό)</label>
                                <select
                                    id="topic-select"
                                    className="topic-select"
                                    value={selectedTopicId}
                                    onChange={(e) => setSelectedTopicId(e.target.value)}
                                    disabled={isGenerating}
                                >
                                    <option value="">Αυτόματη επιλογή</option>
                                    {topics.map((topic) => (
                                        <option key={topic.id} value={topic.id}>
                                            {topic.name}
                                        </option>
                                    ))}
                                </select>
                                <p className="topic-description">
                                    {selectedTopic ? selectedTopic.description : "Το σύστημα θα επιλέξει αυτόματα μια ενότητα."}
                                </p>
                            </div>
                        )}

                        <div className="modal-actions">
                            <button
                                type="button"
                                className="cancel-btn"
                                onClick={onClose}
                                disabled={isGenerating}
                            >
                                Ακύρωση
                            </button>
                            <button
                                type="submit"
                                className="generate-btn"
                                disabled={isGenerating}
                            >
                                {isGenerating ? 'Δημιουργία άσκησης...' : 'Δημιουργία'}
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    );
}