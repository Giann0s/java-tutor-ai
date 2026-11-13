import { createContext, useState, useEffect, startTransition } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axiosConfig";

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('access_token'));
    const [profile, setProfile] = useState({});
    const navigate = useNavigate();

    useEffect(() => {
        if (!token) return;

        const fetchProfile = async () => {
            try {
                const response = await api.get('/users/profile');
                setProfile(response.data);
            } catch (error) {
                console.error("Σφάλμα στην φόρτωση του προφίλ: ", error);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                setToken(null);
            }
        };

        fetchProfile();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const isProfessor = profile?.role === 'professor';
    const isAdmin = profile?.role === 'admin';

    const login = async (newAccessToken, newRefreshToken) => {
        localStorage.setItem('access_token', newAccessToken);
        if (newRefreshToken) {
            localStorage.setItem('refresh_token', newRefreshToken);
        }

        try {
            const response = await api.get('/users/profile', {
                headers: { Authorization: `Bearer ${newAccessToken}` }
            });
            const userProfile = response.data;

            startTransition(() => {
                setProfile(userProfile);
                setToken(newAccessToken);
                navigate(userProfile.role === 'admin' ? '/admin' : '/home', { replace: true });

            })

            return userProfile;
        } catch (error) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        startTransition(() => {
            setProfile({});
            setToken(null);
            navigate('/login', { replace: true });
        })
    };

    return (
        <AuthContext.Provider value={{ token, login, logout, profile, setProfile, isProfessor, isAdmin }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
