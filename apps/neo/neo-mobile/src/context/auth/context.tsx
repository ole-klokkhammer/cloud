import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { handleLogin, handleLogout } from '@/services/auth/authentication';
import { isTokenExpired } from '@/services/auth/token';

interface AuthContextType {
    initializing: boolean;
    authenticated: boolean;
    login: () => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [authenticated, setAuthenticated] = useState(false);

    // used to check if the app is still loading - to prevent redirecting before the app is ready
    const [initializing, setInitializing] = useState(true);

    const login = () => handleLogin().finally(() => {
        checkAuth();
    });

    const logout = () => handleLogout().finally(() => {
        checkAuth();
    });

    const checkAuth = async () => {
        console.log('isAuthenticated', 'checking');
        const isExpired = await isTokenExpired();
        console.log('isExpired', isExpired);
        setAuthenticated(!isExpired);
        setInitializing(false);
    };

    useEffect(() => {
        checkAuth();
    }, []);

    return (
        <AuthContext.Provider value={{ initializing, authenticated, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};