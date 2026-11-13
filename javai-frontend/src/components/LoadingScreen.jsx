import './LoadingScreen.css';

export function LoadingScreen() {
    return (
        <div className="loading-screen-container">
            <div className="app-logo loading-logo">
                Jav<span>AI</span>
            </div>
            <div className="loading-text">Φόρτωση...</div>
        </div>
    );
}