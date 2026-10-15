import './ChatMessage.css';

export function ChatMessage({ sender_role, content, time }) {

    const isModel = sender_role === 'model';

    return (
        <div className={`message-row ${isModel ? "model-row" : "user-row"}`}>
            <div className={`message-bubble ${isModel ? "model-bubble" : "user-bubble"}`}>
                <div className="message-content">
                    {content}
                </div>
                <div className="message-time">
                    {time}
                </div>
            </div>
        </div>
    )
}