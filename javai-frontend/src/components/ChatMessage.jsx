import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';
import LoadingSpinner from '../assets/loading-spinner2.gif';

export function ChatMessage({ sender_role, content, time, isLoading = false }) {

    const isModel = sender_role === 'model';

    if (isLoading) {
        return (
            <div className="message-row model-row">
                <img className="loading-spinner" alt="Φόρτωση..." src={LoadingSpinner} />
            </div>
        );
    }

    return (
        <div className={`message-row ${isModel ? "model-row" : "user-row"}`}>
            <div className={`message-bubble ${isModel ? "model-bubble" : "user-bubble"}`}>
                {isModel ? (
                    <div className="message-content markdown-body">
                        <ReactMarkdown>{content}</ReactMarkdown>
                    </div>
                ) : (
                    <div className="message-content user-text">
                        {content}
                    </div>
                )}

                <div className="message-time">
                    {time}
                </div>
            </div>
        </div>
    )
}