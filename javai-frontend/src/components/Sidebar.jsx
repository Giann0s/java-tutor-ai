import ProfilePic from '../assets/star_guardian_garen_by_marresart_d9tn6yc-fullview.jpg';
import { useContext } from 'react';
import AuthContext from '../context/AuthContext';
import './Sidebar.css';


export function Sidebar() {
    const { logout } = useContext(AuthContext);

    return (
        <aside className="sidebar">
            <div className="app-logo">
                Jav<span>AI</span>
            </div>

            <button className="exercise-btn">Ιστορικό Ασκήσεων</button>
            <button className="new-exercise-btn">Νέα Άσκηση</button>
            <button className="new-conversation-btn">Νέα συζήτηση</button>

            <div className="chat-container">
                <h3>Ιστορικό συζητήσεων</h3>
                <ul>
                    <li>Εισαγωγή στη Java</li>
                    <li>Τι είναι ο Πολυμορφισμός;</li>
                    <li>Διόρθωση σφάλματος NullPointer</li>
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