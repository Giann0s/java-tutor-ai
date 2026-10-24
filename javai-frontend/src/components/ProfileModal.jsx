import './ProfileModal.css';
import { useContext, useState, useEffect } from 'react';
import AuthContext from '../context/AuthContext';
import api from '../api/axiosConfig';

export function ProfileModal({ isOpen, onClose, profile, setProfile }) {
    const { logout } = useContext(AuthContext);

    const [firstName, setFirstName] = useState('');
    const [lastName, setLastName] = useState('');
    const [email, setEmail] = useState('');

    const [oldPassword, setOldPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');

    const [message, setMessage] = useState({ text: '', type: '' });
    const [isSaving, setIsSaving] = useState(false);

    useEffect(() => {
        const fetchCurrentData = () => {
            if (profile && isOpen) {
                setFirstName(profile.first_name || '');
                setLastName(profile.last_name || '');
                setEmail(profile.email || '');
                setMessage({ text: '', type: '' });
                setOldPassword('');
                setNewPassword('');
            }
        }

        fetchCurrentData();

    }, [profile, isOpen]);

    if (!isOpen) return null;

    const handleUpdateInfo = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage({ text: '', type: '' });

        try {
            const response = await api.patch('/users/profile', {
                first_name: firstName,
                last_name: lastName,
                email: email
            })

            setProfile(response.data);
            setMessage({ text: 'Τα στοιχεία ενημερώθηκαν επιτυχώς!', type: 'success' });

        } catch (error) {
            const detail = error.response?.data?.detail || 'Σφάλμα κατά την ενημέρωση στοιχείων.';
            setMessage({ text: detail, type: 'error' });
        } finally {
            setIsSaving(false);
        }
    }

    const handleUpdatePassword = async (e) => {
        e.preventDefault();
        if (!oldPassword || !newPassword) return;

        setIsSaving(true);
        setMessage({ text: '', type: '' });

        try {
            const response = await api.patch('/users/profile/password', {
                current_password: oldPassword,
                new_password: newPassword
            });
            setMessage({ text: response.data.message || 'Ο κωδικός ενημερώθηκε επιτυχώς!', type: 'success' });
            setOldPassword('');
            setNewPassword('');
        } catch (error) {
            const detail = error.response?.data?.detail || 'Λάθος τρέχων κωδικός.';
            setMessage({ text: detail, type: 'error' });
        } finally {
            setIsSaving(false);
        }
    }

    const handleDeleteAccount = async () => {
        const confirmed = window.confirm(
            'Είστε απόλυτα σίγουροι ότι θέλετε να διαγράψετε τον λογαριασμό σας; Αυτή η ενέργεια δεν αναιρείται.'
        );
        if (!confirmed) return;

        try {
            await api.delete('/users/delete');
            logout();
        } catch (error) {
            const detail = error.response?.data?.detail || 'Σφάλμα κατά τη διαγραφή του λογαριασμού.';
            setMessage({ text: detail, type: 'error' });
        }
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="profile-modal-card" onClick={(e) => e.stopPropagation()}>
                <div className="profile-modal-header">
                    <h2>Το Προφίλ μου</h2>
                    <button className="close-modal-btn" onClick={onClose}>&#10005;</button>
                </div>
                {message.text && (
                    <div className={`profile-alert ${message.type === 'success' ? 'alert-success' : 'alert-error'}`}>
                        {message.text}
                    </div>
                )}

                <form onSubmit={handleUpdateInfo} className="profile-form-section">
                    <h3>Προσωπικά Στοιχεία</h3>
                    <div className="form-group">
                        <label>Όνομα</label>
                        <input
                            type="text"
                            value={firstName}
                            onChange={(e) => setFirstName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Επώνυμο</label>
                        <input
                            type="text"
                            value={lastName}
                            onChange={(e) => setLastName(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="save-profile-btn" disabled={isSaving}>
                        Αποθήκευση Στοιχείων
                    </button>
                </form>

                <hr className="modal-divider" />

                <form onSubmit={handleUpdatePassword} className="profile-form-section">
                    <h3>Αλλαγή Κωδικού</h3>
                    <div className="form-group">
                        <label>Τρέχων Κωδικός</label>
                        <input
                            type="password"
                            value={oldPassword}
                            onChange={(e) => setOldPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Νέος Κωδικός</label>
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    <button type="submit" className="save-password-btn" disabled={isSaving}>
                        Ενημέρωση Κωδικού
                    </button>
                </form>

                <hr className="modal-divider" />

                <div className="danger-zone">
                    <button type="button" className="delete-account-btn" onClick={handleDeleteAccount}>
                        Διαγραφή Λογαριασμού
                    </button>
                </div>

            </div>
        </div>
    )
}