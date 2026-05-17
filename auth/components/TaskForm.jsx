import React, { useContext } from 'react';
import { useForm } from '../hooks/useForm';
import { AuthContext } from '../context/AuthContext';

export const TaskForm = ({ addTask }) => {
  const { user } = useContext(AuthContext);
  const [formValues, handleInputChange, reset] = useForm({
    title: ''
  });

  const { title } = formValues;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (title.trim().length <= 1) return;

    // Requisito 2.3: UI Dinámica con el nombre del usuario
    const newTask = {
      id: new Date().getTime(),
      title,
      author: user?.name || 'Desconocido', // Obtenemos el nombre del AuthContext
      status: 'todo'
    };

    if (addTask) addTask(newTask);
    reset();
  };

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <input 
        type="text"
        name="title"
        placeholder="Añadir una nueva tarea..."
        value={title}
        onChange={handleInputChange}
        autoComplete="off"
      />
      <button type="submit">Guardar</button>
    </form>
  );
};
