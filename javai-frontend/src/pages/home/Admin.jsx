import { useState, useEffect, useContext } from 'react';
import AuthContext from '../../context/AuthContext';
import api from '../../api/axiosConfig';
import { ProfileModal } from '../../components/ProfileModal';
import { AdminUserModal } from '../../components/AdminUserModal';
import './Admin.css';

export function Admin() {
    const { profile, setProfile, logout } = useContext(AuthContext);

    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [roleFilter, setRoleFilter] = useState('all');

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [isUserModalOpen, setIsUserModalOpen] = useState(false);
    const [editingUser, setEditingUser] = useState(null);

    const initials = profile?.first_name && profile?.last_name
        ? `${profile.first_name.charAt(0)}${profile.last_name.charAt(0)}`
        : 'A';

    useEffect(() => {
        const fetchUsers = async () => {
            setIsLoading(true);
            setError('');
            try {
                const response = await api.get('/users/');
                setUsers(response.data);
            } catch (err) {
                console.error("Σφάλμα φόρτωσης χρηστών:", err);
                setError("Αδυναμία φόρτωσης της λίστας χρηστών.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchUsers();
    }, []);

    const handleOpenCreate = () => {
        setEditingUser(null);
        setIsUserModalOpen(true);
    };

    const handleOpenEdit = (user) => {
        setEditingUser(user);
        setIsUserModalOpen(true);
    };

    const handleUserSaved = (savedUser, isEdit) => {
        if (isEdit) {
            setUsers((prev) => prev.map((u) => (u.id === savedUser.id ? savedUser : u)));
            if (savedUser.id === profile?.id) {
                setProfile(savedUser);
            }
        } else {
            setUsers((prev) => [...prev, savedUser]);
        }
    };

    const handleDeleteUser = async (userToDelete) => {
        if (!window.confirm(`Είστε σίγουροι ότι θέλετε να διαγράψετε τον χρήστη ${userToDelete.first_name} ${userToDelete.last_name};`)) {
            return;
        }
        try {
            await api.delete(`/users/${userToDelete.id}`);
            setUsers((prev) => prev.filter((u) => u.id !== userToDelete.id));
        } catch (err) {
            alert(err.response?.data?.detail || "Σφάλμα κατά τη διαγραφή του χρήστη.");
        }
    };

    const filteredUsers = roleFilter === 'all'
        ? users
        : users.filter((u) => u.role === roleFilter);

    const totalStudents = users.filter((u) => u.role === 'student').length;
    const totalProfessors = users.filter((u) => u.role === 'professor').length;
    const totalAdmins = users.filter((u) => u.role === 'admin').length;

    const getRoleLabel = (role) => {
        if (role === 'student') return 'Φοιτητής';
        if (role === 'professor') return 'Καθηγητής';
        if (role === 'admin') return 'Admin';
        return role;
    };

    return (
        <div className="admin-layout">
            <header className="admin-header">
                <div className="admin-brand">
                    <div className="admin-logo">
                        Jav<span>AI</span>
                    </div>
                    <span className="admin-badge">Admin Panel</span>
                </div>

                <div className="admin-header-right">
                    <div className="admin-profile-trigger" onClick={() => setIsProfileModalOpen(true)}>
                        <div className="admin-avatar">{initials}</div>
                        <div className="admin-user-info">
                            <p className="admin-user-name">
                                {profile?.first_name ? `${profile.first_name} ${profile.last_name}` : 'Admin'}
                            </p>
                            <p className="admin-user-role">Διαχειριστής</p>
                        </div>
                    </div>
                    <button className="admin-logout-btn" onClick={logout}>
                        Αποσύνδεση
                    </button>
                </div>
            </header>

            <main className="admin-main">
                <div className="admin-container">
                    <div className="admin-stats-grid">
                        <div className="admin-stat-card">
                            <span className="admin-stat-label">Σύνολο Χρηστών</span>
                            <strong className="admin-stat-value">{users.length}</strong>
                        </div>
                        <div className="admin-stat-card">
                            <span className="admin-stat-label">Φοιτητές</span>
                            <strong className="admin-stat-value admin-text-blue">{totalStudents}</strong>
                        </div>
                        <div className="admin-stat-card">
                            <span className="admin-stat-label">Καθηγητές</span>
                            <strong className="admin-stat-value admin-text-amber">{totalProfessors}</strong>
                        </div>
                        <div className="admin-stat-card">
                            <span className="admin-stat-label">Διαχειριστές (Admins)</span>
                            <strong className="admin-stat-value admin-text-green">{totalAdmins}</strong>
                        </div>
                    </div>

                    <div className="admin-toolbar">
                        <div className="admin-filter-tabs">
                            <button
                                className={`admin-filter-tab ${roleFilter === 'all' ? 'active' : ''}`}
                                onClick={() => setRoleFilter('all')}
                            >
                                Όλοι
                            </button>
                            <button
                                className={`admin-filter-tab ${roleFilter === 'student' ? 'active' : ''}`}
                                onClick={() => setRoleFilter('student')}
                            >
                                Φοιτητές
                            </button>
                            <button
                                className={`admin-filter-tab ${roleFilter === 'professor' ? 'active' : ''}`}
                                onClick={() => setRoleFilter('professor')}
                            >
                                Καθηγητές
                            </button>
                            <button
                                className={`admin-filter-tab ${roleFilter === 'admin' ? 'active' : ''}`}
                                onClick={() => setRoleFilter('admin')}
                            >
                                Admins
                            </button>
                        </div>

                        <button className="admin-new-user-btn" onClick={handleOpenCreate}>
                            + Νέος Καθηγητής / Admin
                        </button>
                    </div>

                    <div className="admin-table-card">
                        {isLoading ? (
                            <div className="admin-status-msg">Φόρτωση χρηστών...</div>
                        ) : error ? (
                            <div className="admin-error-msg">{error}</div>
                        ) : filteredUsers.length === 0 ? (
                            <div className="admin-status-msg">Δεν βρέθηκαν χρήστες σε αυτή την κατηγορία.</div>
                        ) : (
                            <table className="admin-users-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Ονοματεπώνυμο</th>
                                        <th>Email</th>
                                        <th>Ρόλος</th>
                                        <th className="admin-actions-col">Ενέργειες</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredUsers.map((u) => (
                                        <tr key={u.id}>
                                            <td className="admin-id-cell">#{u.id}</td>
                                            <td className="admin-name-cell">
                                                {u.first_name} {u.last_name}
                                                {u.id === profile?.id && <span className="admin-you-tag">(Εσείς)</span>}
                                            </td>
                                            <td className="admin-email-cell">{u.email}</td>
                                            <td>
                                                <span className={`admin-role-badge admin-role-${u.role}`}>
                                                    {getRoleLabel(u.role)}
                                                </span>
                                            </td>
                                            <td className="admin-actions-cell">
                                                <button
                                                    type="button"
                                                    className="admin-row-btn admin-edit-btn"
                                                    onClick={() => handleOpenEdit(u)}
                                                    title="Επεξεργασία"
                                                >
                                                    ✎
                                                </button>
                                                <button
                                                    type="button"
                                                    className="admin-row-btn admin-delete-btn"
                                                    onClick={() => handleDeleteUser(u)}
                                                    disabled={u.id === profile?.id}
                                                    title={u.id === profile?.id ? "Δεν μπορείτε να διαγράψετε τον εαυτό σας από εδώ" : "Διαγραφή"}
                                                >
                                                    &#10005;
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </main>

            <AdminUserModal
                isOpen={isUserModalOpen}
                onClose={() => setIsUserModalOpen(false)}
                editingUser={editingUser}
                onUserSaved={handleUserSaved}
            />

            <ProfileModal
                isOpen={isProfileModalOpen}
                onClose={() => setIsProfileModalOpen(false)}
                profile={profile}
                setProfile={setProfile}
            />
        </div>
    );
}