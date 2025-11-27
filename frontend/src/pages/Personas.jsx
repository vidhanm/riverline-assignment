import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import PersonaForm from '../components/PersonaForm';

export default function Personas() {
  const [personas, setPersonas] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingPersona, setEditingPersona] = useState(null);

  useEffect(() => {
    fetchPersonas();
  }, []);

  const fetchPersonas = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/personas/`);
      setPersonas(response.data);
    } catch (error) {
      console.error('Error fetching personas:', error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this persona?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/personas/${id}`);
      fetchPersonas();
    } catch (error) {
      console.error('Error deleting persona:', error);
    }
  };

  const handleEdit = (persona) => {
    setEditingPersona(persona);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingPersona(null);
    fetchPersonas();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Personas</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Create Persona
        </button>
      </div>

      {showForm && (
        <PersonaForm
          persona={editingPersona}
          onClose={handleFormClose}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {personas.map((persona) => (
          <div key={persona.id} className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg">{persona.name}</h3>
            <p className="text-sm text-gray-600">Personality: {persona.personality}</p>
            <p className="text-sm text-gray-600">Mood: {persona.mood}</p>
            <p className="text-sm text-gray-500 mt-2 truncate">{persona.system_prompt}</p>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleEdit(persona)}
                className="text-blue-500 text-sm hover:underline"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(persona.id)}
                className="text-red-500 text-sm hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {personas.length === 0 && !showForm && (
        <p className="text-gray-500 text-center mt-8">No personas yet. Create one to get started!</p>
      )}
    </div>
  );
}
