import './Login.css';
import api from '../../api/axiosConfig';
import { useState, useEffect, useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import AuthContext from '../../context/AuthContext';

export function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();
    const { login } = useContext(AuthContext);
    const location = useLocation();

    const [successMessage, setSuccessMessage] = useState(location.state?.successMessage || ""); //for handling the success message from the register page

    useEffect(() => {
        if (location.state?.successMessage) {
            navigate(location.pathname, {replace: true, state: {}});
        }
    }, [location, navigate]); //for deleting the state so that the success message disappears after reloading

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMessage('');

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await api.post('/auth/login', formData);

            login(response.data.access_token);
            navigate('/home-student');
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