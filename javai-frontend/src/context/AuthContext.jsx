import { createContext, useState, useEffect } from "react";
import api from "../api/axiosConfig";

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('access_token'));
    const [profile, setProfile] = useState({});

    useEffect(() => {
        const fetchProfile = async () => {
            if (!token) {
                setProfile({});
                return;
            }
            try {
                const response = await api.get('/users/profile');
                setProfile(response.data);
            } catch (error) {
                console.error("Σφάλμα στην φόρτωση του προφίλ: ", error);
            }
        };

        fetchProfile();
    }, [token]);

    const isProfessor = profile?.role === 'professor';

    const login = (newAccessToken, newRefreshToken) => {
        localStorage.setItem('access_token', newAccessToken);
        if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
        }
        setToken(newAccessToken);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, profile, setProfile, isProfessor }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
