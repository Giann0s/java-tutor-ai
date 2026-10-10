import './Login.css';
import { useState } from 'react';

export function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    function handleSubmit(e) {
        e.preventDefault();
    }

    return (
        <div className='container'>
            <div className='app-logo'>
                Jav<span>AI</span>
            </div>
            <form onSubmit={handleSubmit}>
                <h2 className='title'>Σύνδεση</h2>
                <div className='inputs'>
                    <input
                        type="email"
                        className="text-input"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => { setEmail(e.target.value); }}
                        required
                    />
                    <input
                        type="password"
                        className="text-input"
                        placeholder="Κωδικός"
                        value={password}
                        onChange={(e) => { setPassword(e.target.value); }}
                        required
                    />
                </div>
                <button type="submit" className="login-btn">Είσοδος</button>
            </form>

            <div className="signup-prompt">
                Δεν έχετε λογαριασμό; <button type="button" className="signup-link">Κάντε εγγραφή τώρα</button>
            </div>
        </div>
    )
}