import { createContext, useState } from "react";

const AuthContext = createContext(); 

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('access_token'));

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
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
