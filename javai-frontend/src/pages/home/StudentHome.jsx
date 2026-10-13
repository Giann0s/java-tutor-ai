import './StudentHome.css';
import { Sidebar } from '../../components/Sidebar.jsx';
import { ChatMessage } from '../../components/ChatMessage.jsx';

export function StudentHome() {

    return (
        <div className="home-layout">
            <Sidebar />

            <main className="main-chat-area">
                <div className="chat-messages">
                    <ChatMessage
                        sender="model"
                        content="Γεια! Πως μπορώ να βοηθήσω;"
                        time="14:40"
                    />
                    <ChatMessage
                        sender="user"
                        content="Μπορείς να μου εξηγήσεις την κληρονομικότητα;"
                        time="14:42"
                    />

                </div>

                <div className="input-wrapper">
                    <input
                        className="chat-input"
                        placeholder="Γράψτε ένα μήνυμα..."
                    />
                    <button className="send-btn">&#10148;</button>
                </div>
            </main>
        </div>
    )

}