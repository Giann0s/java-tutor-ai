import ProfilePic from '../assets/star_guardian_garen_by_marresart_d9tn6yc-fullview.jpg';
import { useContext } from 'react';
import AuthContext from '../context/AuthContext';
import './Sidebar.css';


export function Sidebar({ conversations, currentConvId, setCurrentConvId, handleNewChat, handleDeleteConversation }) {
    const { logout } = useContext(AuthContext);

    return (
        <aside className="sidebar">
            <div className="app-logo">
                Jav<span>AI</span>
            </div>

            <button className="exercise-btn">Ιστορικό Ασκήσεων</button>
            <button className="new-exercise-btn">Νέα Άσκηση</button>
            <button
                className="new-conversation-btn"
                onClick={handleNewChat}
            >
                Νέα συζήτηση
            </button>

            <div className="chat-container">
                <h3>Ιστορικό συζητήσεων</h3>
                <ul>
                    {conversations.map((conv) => (
                        <li
                            key={conv.id}
                            className={`conv-item ${currentConvId === conv.id ? 'active' : ''}`}
                            onClick={() => setCurrentConvId(conv.id)}
                        >
                            <span className="conv-title">{conv.title}</span>

                            <button
                                className="delete-conv-btn"
                                onClick={(e) => {
                                    e.stopPropagation(); //Prevents from clicking the <li> element as well
                                    handleDeleteConversation(conv.id);
                                }}
                            >
                                &#10005;
                            </button>
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