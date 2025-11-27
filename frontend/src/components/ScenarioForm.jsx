import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function ScenarioForm({ scenario, onClose }) {
  const [personas, setPersonas] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    context: '',
    goal: '',
    persona_a_id: '',
    persona_b_id: '',
    max_turns: 10
  });

  useEffect(() => {
    fetchPersonas();
    if (scenario) {
      setFormData(scenario);
    }
  }, [scenario]);

  const fetchPersonas = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/personas/`);
      setPersonas(response.data);
    } catch (error) {
      console.error('Error fetching personas:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = {
        ...formData,
        persona_a_id: parseInt(formData.persona_a_id),
        persona_b_id: parseInt(formData.persona_b_id),
        max_turns: parseInt(formData.max_turns)
      };

      if (scenario) {
        await axios.put(`${API_BASE_URL}/scenarios/${scenario.id}`, data);
      } else {
        await axios.post(`${API_BASE_URL}/scenarios/`, data);
      }
      onClose();
    } catch (error) {
      console.error('Error saving scenario:', error);
      alert('Error saving scenario: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">
          {scenario ? 'Edit' : 'Create'} Scenario
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
            <label className="block text-sm font-medium mb-1">Context *</label>
            <textarea
              required
              value={formData.context}
              onChange={(e) => setFormData({ ...formData, context: e.target.value })}
              className="w-full border rounded px-3 py-2 h-20"
              placeholder="Conversation starter / initial prompt"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Goal</label>
            <textarea
              value={formData.goal}
              onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
              className="w-full border rounded px-3 py-2 h-20"
              placeholder="What should this conversation achieve?"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Persona A *</label>
              <select
                required
                value={formData.persona_a_id}
                onChange={(e) => setFormData({ ...formData, persona_a_id: e.target.value })}
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Select persona</option>
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Persona B *</label>
              <select
                required
                value={formData.persona_b_id}
                onChange={(e) => setFormData({ ...formData, persona_b_id: e.target.value })}
                className="w-full border rounded px-3 py-2"
              >
                <option value="">Select persona</option>
                {personas.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Max Turns</label>
            <input
              type="number"
              min="1"
              max="50"
              value={formData.max_turns}
              onChange={(e) => setFormData({ ...formData, max_turns: e.target.value })}
              className="w-full border rounded px-3 py-2"
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
              {scenario ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
