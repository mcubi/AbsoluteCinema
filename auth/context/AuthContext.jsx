import React, { createContext, useState, useEffect } from 'react';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    // Requisito 2.1: Persistencia de Sesión
    const [user, setUser] = useState(() => {
        const savedUser = localStorage.getItem('user');
        return savedUser ? JSON.parse(savedUser) : null;
    });

    const login = (credential) => {
        // Requisito 1.2: Uso de jwt-decode
        const decodedUser = jwtDecode(credential);
        setUser(decodedUser);
        localStorage.setItem('user', JSON.stringify(decodedUser));
    };

    const logout = () => {
        setUser(null);
        localStorage.removeItem('user');
    };

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
