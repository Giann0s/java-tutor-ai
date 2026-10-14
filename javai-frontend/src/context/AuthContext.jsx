import { createContext, useState } from "react";

const AuthContext = createContext(); 

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem('access_token'));

    const login = (newToken) => {
        localStorage.setItem('access_token', newToken);
        setToken(newToken);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setToken(null);
    };

    return (
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
