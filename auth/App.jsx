import React, { useContext, useEffect } from 'react';
import { AuthContext } from './context/AuthContext';
import { TaskForm } from './components/TaskForm';
import { Column } from './components/Column';
import './App.css';

// ¡IMPORTANTE! Reemplaza este ID con el que creaste en Google Cloud Console
// Este ID debe estar en tu AuthProvider, no aquí.

function App() {
  const { user, logout } = useContext(AuthContext);

  return (
    <div className="App">
      <header className="app-header">
        <h1>Kanban Board</h1>
        {user && (
          <div className="user-profile">
            <img src={user.picture} alt={user.name} className="avatar" />
            <span className="username">{user.name}</span>
            <button className="logout-btn" onClick={logout}>Cerrar Sesión</button>
          </div>
        )}
      </header>

      <main>
        {/* Requisito 2.2: Protección del Tablero */}
        {user ? (
          <div className="board-container">
            <TaskForm />
            {/* Aquí asumo que tus Columnas van renderizadas así */}
            <div className="kanban-columns">
              <Column status="todo" title="Pendientes" />
              <Column status="in-progress" title="En Proceso" />
              <Column status="done" title="Completadas" />
            </div>
          </div>
        ) : (
          <div className="login-message">
            <h2>Acceso Restringido</h2>
            <p>Por favor, inicia sesión con Google para gestionar el tablero.</p>
            {/* One Tap se activará automáticamente si está configurado en tu `index.js` con `<GoogleOAuthProvider>` */}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
