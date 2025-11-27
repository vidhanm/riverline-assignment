import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import ScenarioForm from '../components/ScenarioForm';

export default function Scenarios() {
  const [scenarios, setScenarios] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingScenario, setEditingScenario] = useState(null);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/scenarios/`);
      setScenarios(response.data);
    } catch (error) {
      console.error('Error fetching scenarios:', error);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Delete this scenario?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/scenarios/${id}`);
      fetchScenarios();
    } catch (error) {
      console.error('Error deleting scenario:', error);
    }
  };

  const handleEdit = (scenario) => {
    setEditingScenario(scenario);
    setShowForm(true);
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingScenario(null);
    fetchScenarios();
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Scenarios</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Create Scenario
        </button>
      </div>

      {showForm && (
        <ScenarioForm
          scenario={editingScenario}
          onClose={handleFormClose}
        />
      )}

      <div className="space-y-4">
        {scenarios.map((scenario) => (
          <div key={scenario.id} className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg">{scenario.name}</h3>
            <p className="text-sm text-gray-600">Context: {scenario.context}</p>
            <p className="text-sm text-gray-600">Goal: {scenario.goal}</p>
            <p className="text-sm text-gray-500">Max turns: {scenario.max_turns}</p>
            <div className="mt-4 flex gap-2">
              <button
                onClick={() => handleEdit(scenario)}
                className="text-blue-500 text-sm hover:underline"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(scenario.id)}
                className="text-red-500 text-sm hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {scenarios.length === 0 && !showForm && (
        <p className="text-gray-500 text-center mt-8">No scenarios yet. Create one to get started!</p>
      )}
    </div>
  );
}
