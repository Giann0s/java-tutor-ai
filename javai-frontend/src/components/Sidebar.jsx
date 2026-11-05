import { useContext, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import { ProfileModal } from './ProfileModal';
import { ClassOverviewModal } from './ClassOverviewModal';
import './Sidebar.css';


export function Sidebar({
    mode = "chat",
    items = [], //Stores conversations or exercises
    currentId,
    setCurrentId,
    handleNewAction,
    handleDeleteItem,
    handleNewTopic
}) {
    const { logout, profile, setProfile, isProfessor } = useContext(AuthContext);
    const navigate = useNavigate();

    const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
    const [isOverviewModalOpen, setIsOverviewModalOpen] = useState(false);

    const isChat = mode === "chat";

    const chatRoute = '/home';
    const exerciseRoute = '/exercises';

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
                    onClick={() => navigate(isChat ? exerciseRoute : chatRoute)}
                >
                    {isChat ? 'Ασκήσεις' : 'Συνομιλία'}
                </button>

                {/* Extra button only for the professor */}
                {isProfessor && (
                    <button
                        className="switch-btn"
                        onClick={() => setIsOverviewModalOpen(true)}
                    >
                        Επισκόπηση Τάξης
                    </button>
                )}


                {/* Button for creating new conversation/exercise */}
                <button
                    className="new-item-btn"
                    onClick={handleNewAction}
                >
                    {isChat ? 'Νέα Συζήτηση' : 'Νέα Άσκηση'}
                </button>


                {isProfessor && mode === "exercises" && handleNewTopic && (
                    <button
                        className="new-item-btn"
                        onClick={handleNewTopic}
                    >
                        Κεφάλαια
                    </button>
                )}

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
                                    {!isChat && item.is_public ? `✒ ${item.title}` : item.title}
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

            {isProfessor && (
                <ClassOverviewModal
                    isOpen={isOverviewModalOpen}
                    onClose={() => setIsOverviewModalOpen(false)}
                />
            )}
        </>
    )

}