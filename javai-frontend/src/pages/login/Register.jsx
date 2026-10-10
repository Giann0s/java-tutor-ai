import { useState } from "react";
import './Register.css';

export function Register() {
    const [name, setName] = useState("");
    const [lastName, setLastName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    function handleSubmit(e) {
        e.preventDefault();
        console.log(name, lastName, email, password);
    }

    return (
        <div className="container">
            <div className="app-logo">
                Jav<span>AI</span>
            </div>

            <form onSubmit={handleSubmit}>
                <h2 className="title">Εγγραφή</h2>

                <div className="inputs">
                    <input
                        type="text"
                        className="text-input"
                        placeholder="Όνομα"
                        value={name}
                        onChange={(e) => {setName(e.target.value)}}
                        required
                     />

                     <input
                        type="text"
                        className="text-input"
                        placeholder="Επίθετο"
                        value={lastName}
                        onChange={(e) => {setLastName(e.target.value)}}
                        required
                     />

                     <input
                        type="email"
                        className="text-input"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => {setEmail(e.target.value)}}
                        required
                     />

                     <input
                        type="password"
                        className="text-input"
                        placeholder="Κωδικός"
                        value={password}
                        onChange={(e) => {setPassword(e.target.value)}}
                        required
                     />
                </div>
                <button type="submit" className="register-btn">Εγγραφή</button>
            </form>

            <div className="login-prompt">
                Έχετε ήδη λογαριασμό; <button type="button" className="login-link">Συνδεθείτε εδώ</button>
            </div>

        </div>
    )
}