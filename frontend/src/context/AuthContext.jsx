import { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, login as loginApi, logout as logoutApi } from '../api/auth';
import { toDisplayMessage } from '../utils/toDisplayMessage';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const userData = await getCurrentUser();
                setUser(userData);
            } catch (error) {
                localStorage.removeItem('access_token'); // safe string
                localStorage.removeItem('refresh_token');
            }
        }
        setLoading(false);
    };

    const login = async (email, password) => {
        try {
            const data = await loginApi(email, password);
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            const userData = await getCurrentUser();
            setUser(userData);
            navigate('/');
        } catch (error) {
            // Throw string so consumer (Login.jsx) doesn't get object
            throw toDisplayMessage(error);
        }
    };

    const logout = async () => {
        try {
            await logoutApi();
        } catch (error) {
            // Ignore errors
        }
        setUser(null);
        navigate('/login');
    };

    const hasRole = (roles) => {
        if (!user) return false;
        if (typeof roles === 'string') {
            return user.role === roles;
        }
        return roles.includes(user.role);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, hasRole }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
