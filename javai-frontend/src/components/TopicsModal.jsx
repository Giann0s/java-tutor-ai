import './TopicsModal.css';
import { useState } from 'react';
import api from '../api/axiosConfig';

export function TopicsModal({ isOpen, onClose, topics, setTopics }) {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const resetForm = () => {
        setName('');
        setDescription('');
        setEditingId(null);
        setError('');
    };

    const handleEditClick = (topic) => {
        setEditingId(topic.id);
        setName(topic.name);
        setDescription(topic.description || '');
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name.trim() || !description.trim()) return;

        setIsSaving(true);
        setError('');

        try {
            if (editingId) {
                const response = await api.patch(`/topics/${editingId}`, {
                    name: name.trim(),
                    description: description.trim()
                });
                setTopics((prev) => prev.map((t) => (t.id === editingId ? response.data : t)));
            } else {
                const response = await api.post('/topics/', {
                    name: name.trim(),
                    description: description.trim()
                });
                setTopics((prev) => [...prev, response.data]);
            }
            resetForm();
        } catch (err) {
            setError(err.response?.data?.detail || "Σφάλμα κατά την αποθήκευση του κεφαλαίου.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleDelete = async (topicId) => {
        if (!window.confirm("Είστε σίγουροι ότι θέλετε να διαγράψετε αυτό το κεφάλαιο;")) return;
        try {
            await api.delete(`/topics/${topicId}`);
            setTopics((prev) => prev.filter((t) => t.id !== topicId));
            if (editingId === topicId) resetForm();
        } catch (err) {
            alert(err.response?.data?.detail || "Σφάλμα κατά τη διαγραφή του κεφαλαίου.");
        }
    };

    return (
        <div className="modal-overlay" onClick={!isSaving ? onClose : undefined}>
            <div className="modal-content topics-modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Διαχείριση Κεφαλαίων Ύλης</h2>
                    <button className="modal-close-btn" onClick={onClose} disabled={isSaving}>
                        &#10005;
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="modal-form">
                    {error && <p className="topic-error-msg">{error}</p>}

                    <div className="form-group">
                        <label>{editingId ? 'Επεξεργασία Κεφαλαίου' : 'Νέο Κεφάλαιο'}</label>
                        <input
                            type="text"
                            className="topic-input"
                            placeholder="Όνομα Κεφαλαίου"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            disabled={isSaving}
                            required
                        />
                        <textarea
                            className="topic-textarea"
                            placeholder="Περιγραφή κεφαλαίου..."
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            disabled={isSaving}
                            rows={3}
                            required
                        />
                    </div>

                    <div className="modal-actions">
                        {editingId && (
                            <button type="button" className="cancel-btn" onClick={resetForm} disabled={isSaving}>
                                Ακύρωση Επεξεργασίας
                            </button>
                        )}
                        <button type="submit" className="generate-btn" disabled={isSaving}>
                            {isSaving ? 'Αποθήκευση...' : editingId ? 'Ενημέρωση' : 'Προσθήκη Κεφαλαίου'}
                        </button>
                    </div>
                </form>

                <div className="topics-list-section">
                    <h4 className="topics-list-title">
                        Υπάρχοντα Κεφάλαια ({topics.length})
                    </h4>
                    <div className="topics-list-container">
                        {topics.map((t) => (
                            <div key={t.id} className="topic-item-card">
                                <div className="topic-item-info">
                                    <strong className="topic-item-name">{t.name}</strong>
                                    <span className="topic-item-desc">{t.description}</span>
                                </div>
                                <div className="topic-item-actions">
                                    <button
                                        type="button"
                                        className="topic-action-btn edit-btn"
                                        onClick={() => handleEditClick(t)}
                                        title="Επεξεργασία"
                                    >
                                        ✎
                                    </button>
                                    <button
                                        type="button"
                                        className="topic-action-btn delete-btn"
                                        onClick={() => handleDelete(t.id)}
                                        title="Διαγραφή"
                                    >
                                        &#10005;
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}