import './NewExerciseModal.css';
import { useState } from 'react';

export function NewExerciseModal({ isOpen, onClose, topics, onGenerate, isGenerating }) {
    const [exerciseType, setExerciseType] = useState('mcq');
    const [selectedTopicId, setSelectedTopicId] = useState('');

    if (!isOpen) return null;

    //Get the topic object in order to get the description
    const selectedTopic = topics.find((t) => t.id === Number(selectedTopicId));

    const handleSubmit = (e) => {
        e.preventDefault();
        const topicToSend = selectedTopic ? Number(selectedTopicId) : null;
        onGenerate(exerciseType, topicToSend);
    };

    return (
        <div className="modal-overlay" onClick={!isGenerating ? onClose : undefined}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Δημιουργία Νέας Άσκησης</h2>
                    <button
                        className="modal-close-btn"
                        onClick={onClose}
                        disable={isGenerating}
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