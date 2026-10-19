import './ChatMessage.css';
import ReactMarkdown from 'react-markdown';

export function ChatMessage({ sender_role, content, time }) {

    const isModel = sender_role === 'model';

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