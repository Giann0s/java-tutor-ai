import { useState, useEffect } from 'react';
import api from '../api/axiosConfig';
import './AdminUserModal.css';

export function AdminUserModal({ isOpen, onClose, editingUser, onUserSaved }) {
    const isEditMode = Boolean(editingUser);

    const [role, setRole] = useState('professor');
    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        const handleUser = () => {
            if (editingUser) {
                setFirstName(editingUser.first_name || '');
                setLastName(editingUser.last_name || '');
                setEmail(editingUser.email || '');
                setError('');
            } else {
                setRole('professor');
                setFirstName('');
                setLastName('');
                setEmail('');
                setPassword('');
                setError('');
            }
        }

        handleUser();

    }, [editingUser, isOpen]);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            if (isEditMode) {
                const response = await api.patch(`/users/${editingUser.id}`, {
                    first_name: firstName.trim(),
                    last_name: lastName.trim(),
                    email: email.trim()
                });
                onUserSaved(response.data, true);
            } else {
                const endpoint = role === 'professor' ? '/users/register/professor' : '/users/register/admin';
                const response = await api.post(endpoint, {
                    first_name: firstName.trim(),
                    last_name: lastName.trim(),
                    email: email.trim(),
                    password: password
                });
                onUserSaved(response.data, false);
            }
            onClose();
        } catch (err) {
            setError(err.response?.data?.detail || "Σφάλμα κατά την αποθήκευση του χρήστη.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="admin-modal-overlay" onClick={!isSubmitting ? onClose : undefined}>
            <div className="admin-modal-card" onClick={(e) => e.stopPropagation()}>
                <div className="admin-modal-header">
                    <h2>{isEditMode ? `Επεξεργασία Χρήστη #${editingUser.id}` : 'Δημιουργία Νέου Χρήστη'}</h2>
                    <button className="admin-modal-close-btn" onClick={onClose} disabled={isSubmitting}>
                        &#10005;
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="admin-modal-form">
                    {error && <p className="admin-modal-error">{error}</p>}

                    {!isEditMode && (
                        <div className="admin-form-group">
                            <label>Ρόλος Νέου Χρήστη</label>
                            <div className="admin-role-selector">
                                <button
                                    type="button"
                                    className={`admin-role-card ${role === 'professor' ? 'active' : ''}`}
                                    onClick={() => setRole('professor')}
                                    disabled={isSubmitting}
                                >
                                    <span className="admin-role-title">Καθηγητής</span>
                                    <span className="admin-role-desc">Δημιουργία ασκήσεων & διαχείριση ύλης</span>
                                </button>
                                <button
                                    type="button"
                                    className={`admin-role-card ${role === 'admin' ? 'active' : ''}`}
                                    onClick={() => setRole('admin')}
                                    disabled={isSubmitting}
                                >
                                    <span className="admin-role-title">Admin</span>
                                    <span className="admin-role-desc">Διαχείριση χρηστών του συστήματος</span>
                                </button>
                            </div>
                        </div>
                    )}

                    <div className="admin-form-row">
                        <div className="admin-form-group">
                            <label>Όνομα</label>
                            <input
                                type="text"
                                className="admin-form-input"
                                placeholder="π.χ. Γιώργος"
                                value={firstName}
                                onChange={(e) => setFirstName(e.target.value)}
                                disabled={isSubmitting}
                                required
                            />
                        </div>
                        <div className="admin-form-group">
                            <label>Επώνυμο</label>
                            <input
                                type="text"
                                className="admin-form-input"
                                placeholder="π.χ. Παπαδόπουλος"
                                value={lastName}
                                onChange={(e) => setLastName(e.target.value)}
                                disabled={isSubmitting}
                                required
                            />
                        </div>
                    </div>

                    <div className="admin-form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            className="admin-form-input"
                            placeholder="user@example.com"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            disabled={isSubmitting}
                            required
                        />
                    </div>

                    {!isEditMode && (
                        <div className="admin-form-group">
                            <label>Κωδικός Πρόσβασης (τουλάχιστον 6 χαρακτήρες)</label>
                            <input
                                type="password"
                                className="admin-form-input"
                                placeholder="••••••••"
                                minLength={6}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                disabled={isSubmitting}
                                required
                            />
                        </div>
                    )}

                    <div className="admin-modal-actions">
                        <button type="button" className="admin-cancel-btn" onClick={onClose} disabled={isSubmitting}>
                            Ακύρωση
                        </button>
                        <button type="submit" className="admin-submit-btn" disabled={isSubmitting}>
                            {isSubmitting ? 'Αποθήκευση...' : isEditMode ? 'Αποθήκευση Αλλαγών' : 'Δημιουργία Χρήστη'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}