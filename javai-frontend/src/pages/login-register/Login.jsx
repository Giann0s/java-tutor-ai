import './Login.css';
import axios from 'axios';
import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();
    const location = useLocation();

    const [successMessage, setSuccessMessage] = useState(location.state?.successMessage || ""); //for handling the success message from the register page

    useEffect(() => {
        if (location.state?.successMessage) {
            navigate(location.pathname, {replace: true, state: {}});
        }
    }, [location, navigate]); //for deleting the state so that the success message disappears after reloading

    async function handleSubmit(e) {
        e.preventDefault();
        setError('');
        setSuccessMessage('');

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await axios.post('http://localhost:8000/auth/login', formData);

            localStorage.setItem('access_token', response.data.access_token);

            console.log("Success", response.data);
            //redirection to home page to be added
        } catch (error) {
            if (error.response) {
                setError("Λάθος email ή κωδικός. Δοκιμάστε ξανά.");
                setEmail('');
                setPassword('');
            } else {
                setError("Σφάλμα σύνδεσης.");
                setEmail('');
                setPassword('');
            }
        }
    };

    return (
        <>
            <title>Σύνδεση</title>

            <div className='container'>
                <div className='app-logo'>
                    Jav<span>AI</span>
                </div>
                <form onSubmit={handleSubmit}>
                    <h2 className='title'>Σύνδεση</h2>
                    {error && <div className="error-message">{error}</div>}
                    {successMessage && <div className="success-message">{successMessage}</div>}
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
                    Δεν έχετε λογαριασμό; <button type="button" className="signup-link" onClick={() => { navigate('/register') }}>Κάντε εγγραφή τώρα</button>
                </div>
            </div>
        </>
    )
}