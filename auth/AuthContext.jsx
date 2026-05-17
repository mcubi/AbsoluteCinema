import React, { createContext, useState, useEffect } from 'react';
import { GoogleOAuthProvider, googleLogout } from '@react-oauth/google';
import { useGoogleOneTapLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext(null);

// ¡IMPORTANTE! Reemplaza este ID con el que creaste en Google Cloud Console
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  // Función para iniciar sesión en el backend de Django
  const loginWithBackend = async (credential) => {
    try {
      const response = await fetch('/users/api/auth/google/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credential }),
      });


      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Error en el inicio de sesión del backend');
      }

      const data = await response.json();
      console.log('Backend response:', data.message);

      // Si el backend confirma el login, redirigimos a la home.
      // Django se encargará de servir la página con la sesión de usuario ya iniciada.
      if (data.status === 'success') {
        window.location.href = '/';
      }

    } catch (error) {
      console.error("Error al iniciar sesión con el backend:", error);
      setUser(null);
    }
  };

  // Hook para el login con Google One Tap
  useGoogleOneTapLogin({
    onSuccess: credentialResponse => {
      console.log("Google One Tap success");
      loginWithBackend(credentialResponse.credential);
    },
    onError: () => {
      console.log('Google One Tap login failed');
    },
    disabled: !!user, // Deshabilita One Tap si ya hay un usuario
  });

  const logout = () => {
    googleLogout();
    setUser(null);
    // Opcional: También puedes llamar a tu endpoint de logout de Django
    // fetch('/users/logout', { method: 'POST' });
    console.log("Sesión cerrada");
  };

  const authContextValue = {
    user,
    login: loginWithBackend, // Aunque lo llama One Tap, lo exponemos por si acaso
    logout,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};