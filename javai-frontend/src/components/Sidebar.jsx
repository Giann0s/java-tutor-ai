import { useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import api from '../api/axiosConfig';
import { ProfileModal } from './ProfileModal';
import './Sidebar.css';


export function Sidebar({
    mode = "chat",
    items = [], //Stores conversations or exercises
    currentId,
    setCurrentId,
    handleNewAction,
    handleDeleteItem
}) {
    const { token, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const [profile, setProfile] = useState({});
    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await api.get('/users/profile');
                setProfile(response.data);
            } catch (error) {
                console.error("Σφάλμα στην φόρτωση του προφίλ: ", error);
            }
        };

        if (token) {
            fetchProfile();
        }

    }, [token]);

    const isChat = mode === "chat";

    const initials = profile?.first_name && profile?.last_name ? `${profile.first_name.charAt(0)}${profile.last_name.charAt(0)}` : 'U';

    return (
        <>
            <aside className="sidebar">
                <div className="app-logo">
                    Jav<span>AI</span>
                </div>

                {/* Button for switching between exercise page and chat page */}
                <button
                    className="switch-btn"
                    onClick={() => navigate(isChat ? '/exercises' : '/home-student')}
                >
                    {isChat ? 'Ασκήσεις' : 'Συνομιλία'}
                </button>

                {/* Button for creating new conversation/exercise */}
                <button
                    className="new-item-btn"
                    onClick={handleNewAction}
                >
                    {isChat ? 'Νέα Συζήτηση' : 'Νέα Άσκηση'}
                </button>

                <div className="chat-container">
                    <h3>{isChat ? "Ιστορικό συζητήσεων" : "Ιστορικό ασκήσεων"}</h3>
                    <ul>
                        {items.map((item) => (
                            <li
                                key={item.id}
                                className={`item ${currentId === item.id ? 'active' : ''}`}
                                onClick={() => setCurrentId(item.id)}
                            >
                                <span className="item-title">
                                    {!isChat && item.is_public ? `🎓 ${item.title}` : item.title}
                                </span>

                                {isChat && handleDeleteItem && (
                                    <button
                                        className="delete-item-btn"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteItem(item.id);
                                        }}
                                    >
                                        &#10005;
                                    </button>
                                )}

                            </li>
                        ))}

                    </ul>
                </div>
                <div className="profile-container" onClick={() => setIsProfileModalOpen(true)}>
                    <div className="profile-avatar">{initials}</div>
                    <div className="user-info">
                        <p className="user-name">
                            {profile.first_name ? `${profile.first_name} ${profile.last_name}` : "Φόρτωση..."}
                        </p>
                        <p className="user-role">{profile?.role === "student" ? "Φοιτητής" : "Καθηγητής"}</p>
                    </div>
                    <button onClick={(e) => { e.stopPropagation(); logout(); }} className="logout-btn">
                        Αποσύνδεση
                    </button>

                </div>
            </aside>

            <ProfileModal
                isOpen={isProfileModalOpen}
                onClose={() => setIsProfileModalOpen(false)}
                profile={profile}
                setProfile={setProfile}
            />
        </>
    )

}