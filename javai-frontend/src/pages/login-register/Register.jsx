import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from '../../api/axiosConfig';
import './Register.css';

export function Register() {
    const [name, setName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        const data = {
            first_name: name,
            last_name: lastName,
            email: email,
            password: password
        };

        try {
            await api.post('/users/register/student', data);
            navigate('/login', {
                state: {successMessage: "Επιτυχής εγγραφή! Μπορείτε πλέον να συνδεθείτε."}
            });
        } catch (error) {
            if (error.response) {
                setError("Αυτό το email υπάρχει ήδη.");
                setEmail('');
                setPassword('');
            } else {
                setError("Σφάλμα σύνδεσης.");
                setName('');
                setLastName('');
                setEmail('');
                setPassword('');
            }
        }
    }

    return (
        <>
            <title>Εγγραφή</title>

            <div className="container">
                <div className="app-logo">
                    Jav<span>AI</span>
                </div>

                <form onSubmit={handleSubmit}>
                    <h2 className="title">Εγγραφή</h2>
                    {error && <div className="error-message">{error}</div>}

                    <div className="inputs">
                        <input
                            type="text"
                            className="text-input"
                            placeholder="Όνομα"
                            value={name}
                            onChange={(e) => { setName(e.target.value) }}
                            required
                        />

                        <input
                            type="text"
                            className="text-input"
                            placeholder="Επίθετο"
                            value={lastName}
                            onChange={(e) => { setLastName(e.target.value) }}
                            required
                        />

                        <input
                            type="email"
                            className="text-input"
                            placeholder="Email"
                            value={email}
                            onChange={(e) => { setEmail(e.target.value) }}
                            required
                        />

                        <input
                            type="password"
                            className="text-input"
                            placeholder="Κωδικός"
                            value={password}
                            onChange={(e) => { setPassword(e.target.value) }}
                            required
                        />
                    </div>
                    <button type="submit" className="register-btn">Εγγραφή</button>
                </form>

                <div className="login-prompt">
                    Έχετε ήδη λογαριασμό; <button type="button" className="login-link" onClick={() => { navigate('/login') }}>Συνδεθείτε εδώ</button>
                </div>

            </div>
        </>
    )
}