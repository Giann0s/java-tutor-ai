import './StudentHome.css';
import { Sidebar } from '../../components/Sidebar.jsx';
import { ChatMessage } from '../../components/ChatMessage.jsx';
import { useContext, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../api/axiosConfig';
import AuthContext from '../../context/AuthContext.jsx';
import { formatTime } from '../../utils/formatTime.js';

export function StudentHome() {
    const { token } = useContext(AuthContext);
    const navigate = useNavigate();

    const [conversations, setConversations] = useState([]);
    const [currentConvId, setCurrentConvId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState("");
    const [isSending, setIsSending] = useState(false); // for preventing new messages while the AI is answering

    useEffect(() => {
        if (!token) {
            navigate('/login');
        }
    }, [token, navigate]);

    //GET all conversations
    useEffect(() => {
        const fetchConversations = async () => {
            try {
                const response = await api.get('/chat/');
                setConversations(response.data);
            } catch (error) {
                console.error("Σφάλμα στην φόρτωηση συζητήσεων: ", error);
            }
        };
        if (token) {
            fetchConversations();
        }
    }, [token]);

    //GET a conversation's messages
    useEffect(() => {
        const fetchMessages = async (conversation_id) => {
            try {
                const response = await api.get(`/chat/${conversation_id}/messages`);
                setMessages(response.data);
            } catch (error) {
                console.error("Σφάλα στην φόρτωση μηνυμάτων: ", error);
            }
        };

        if (currentConvId !== null) {
            fetchMessages(currentConvId);
        }
    }, [currentConvId]);

    const handleNewChat = () => {
        setCurrentConvId(null);
        setMessages([]);
    }

    //POST a new message or create a new conversation if currentConvId === null
    const handleSendMessage = async () => {
        if (inputValue.trim() === "" || isSending) return;

        const userText = inputValue;
        setInputValue("");
        setIsSending(true);

        // For adding the user's message instantly on the screen 
        const tempUserMsg = {
            id: crypto.randomUUID(), //temporary ID for showing the message instanly on screen
            sender_role: "user",
            content: userText,
            created_at: new Date().toISOString()
        };
        setMessages((prev) => [...prev, tempUserMsg]);

        try {
            const payload = {
                conversation_id: currentConvId ?? 0,
                user_text: userText
            }

            const response = await api.post('/chat/', payload);
            const modelMsg = {
                id: crypto.randomUUID(),
                sender_role: "model",
                content: response.data.ai_response,
                created_at: new Date().toISOString()
            };
            setMessages((prev) => [...prev, modelMsg]);

            if (currentConvId === null) {
                const newConv = {
                    id: response.data.conversation_id,
                    title: response.data.title
                }
                setConversations((prev) => [newConv, ...prev]);
                setCurrentConvId(response.data.conversation_id);
            }
        } catch (error) {
            console.error("Σφάλμα κατά την αποστολή: ", error);
        } finally {
            setIsSending(false);
        }
    };

    //DELETE a conversation 
    const handleDeleteConversation = async (idToDelete) => {
        try {
            await api.delete(`/chat/${idToDelete}`);
            setConversations((prev) => prev.filter(conv => conv.id !== idToDelete));

            if (currentConvId === idToDelete) {
                handleNewChat();
            }
        } catch (error) {
            console.error("Σφάλμα κατά την διαγραφή: ", error);
        }
    };

    if (!token) return null;

    return (
        <div className="home-layout">
            <Sidebar
                mode="chat"
                items={conversations}
                currentId={currentConvId}
                setCurrentId={setCurrentConvId}
                handleNewAction={handleNewChat}
                handleDeleteItem={handleDeleteConversation}
            />

            <main className="main-chat-area">
                <div className="chat-messages">
                    {messages.map((msg) => (
                        <ChatMessage
                            key={msg.id}
                            sender_role={msg.sender_role}
                            content={msg.content}
                            time={formatTime(msg.created_at)}
                        />
                    ))}

                </div>

                <div className="input-wrapper">
                    <input
                        className="chat-input"
                        placeholder="Γράψτε ένα μήνυμα..."
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                        disabled={isSending}
                    />
                    <button
                        className="send-btn"
                        onClick={handleSendMessage}
                        disabled={isSending}
                    >
                        &#10148;
                    </button>
                </div>
            </main>
        </div>
    )

}