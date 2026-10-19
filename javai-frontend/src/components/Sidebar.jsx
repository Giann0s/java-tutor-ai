import ProfilePic from '../assets/star_guardian_garen_by_marresart_d9tn6yc-fullview.jpg';
import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../context/AuthContext';
import './Sidebar.css';


export function Sidebar({
    mode = "chat",
    items = [], //Stores conversations or exercises
    currentId,
    setCurrentId,
    handleNewAction,
    handleDeleteItem
}) {
    const { logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const isChat = mode === "chat";

    return (
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
            <div className="profile-container">
                <img className="profile-pic" src={ProfilePic} />
                <span>Φοιτητής</span>
                <button onClick={logout} className="logout-btn">
                    Αποσύνδεση
                </button>

            </div>
        </aside>
    )

}