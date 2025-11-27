import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function PersonaForm({ persona, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    personality: '',
    mood: '',
    voice_id: '',
    system_prompt: ''
  });

  useEffect(() => {
    if (persona) {
      setFormData(persona);
    }
  }, [persona]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (persona) {
        await axios.put(`${API_BASE_URL}/personas/${persona.id}`, formData);
      } else {
        await axios.post(`${API_BASE_URL}/personas/`, formData);
      }
      onClose();
    } catch (error) {
      console.error('Error saving persona:', error);
      alert('Error saving persona');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {persona ? 'Edit' : 'Create'} Persona
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Personality</label>
            <input
              type="text"
              value={formData.personality}
              onChange={(e) => setFormData({ ...formData, personality: e.target.value })}
              className="w-full border rounded px-3 py-2"
              placeholder="e.g., friendly, curious, analytical"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Mood</label>
            <input
              type="text"
              value={formData.mood}
              onChange={(e) => setFormData({ ...formData, mood: e.target.value })}
              className="w-full border rounded px-3 py-2"
              placeholder="e.g., happy, excited, calm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Voice ID</label>
            <input
              type="text"
              value={formData.voice_id}
              onChange={(e) => setFormData({ ...formData, voice_id: e.target.value })}
              className="w-full border rounded px-3 py-2"
              placeholder="For TTS (Phase 4)"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">System Prompt *</label>
            <textarea
              required
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              className="w-full border rounded px-3 py-2 h-32"
              placeholder="You are..."
            />
          </div>

          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded hover:bg-gray-100"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              {persona ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
