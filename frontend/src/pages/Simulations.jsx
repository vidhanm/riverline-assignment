import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import AudioPlayer from '../components/AudioPlayer';

export default function Simulations() {
  const [simulations, setSimulations] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState('');

  useEffect(() => {
    fetchSimulations();
    fetchScenarios();
  }, []);

  const fetchSimulations = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulations/`);
      setSimulations(response.data);
    } catch (error) {
      console.error('Error fetching simulations:', error);
    }
  };

  const fetchScenarios = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/scenarios/`);
      setScenarios(response.data);
    } catch (error) {
      console.error('Error fetching scenarios:', error);
    }
  };

  const runSimulation = async () => {
    if (!selectedScenario) {
      alert('Please select a scenario');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/simulations/run?scenario_id=${selectedScenario}`);
      setSelectedRun(response.data);
      fetchSimulations();
    } catch (error) {
      console.error('Error running simulation:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const viewSimulation = async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulations/${id}`);
      setSelectedRun(response.data);
    } catch (error) {
      console.error('Error loading simulation:', error);
    }
  };

  const deleteSimulation = async (id) => {
    if (!confirm('Delete this simulation?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/simulations/${id}`);
      fetchSimulations();
      if (selectedRun?.id === id) setSelectedRun(null);
    } catch (error) {
      console.error('Error deleting simulation:', error);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Simulations</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Run new simulation + List */}
        <div className="lg:col-span-1 space-y-6">
          {/* Run Simulation */}
          <div className="border rounded-lg p-4">
            <h2 className="font-semibold mb-3">Run New Simulation</h2>
            <select
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
              className="w-full border rounded px-3 py-2 mb-3"
            >
              <option value="">Select scenario...</option>
              {scenarios.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <button
              onClick={runSimulation}
              disabled={loading}
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
            >
              {loading ? 'Running...' : 'Run Simulation'}
            </button>
          </div>

          {/* Simulation List */}
          <div className="border rounded-lg p-4">
            <h2 className="font-semibold mb-3">History ({simulations.length})</h2>
            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {simulations.map((sim) => (
                <div
                  key={sim.id}
                  className={`p-3 border rounded cursor-pointer hover:bg-gray-50 ${
                    selectedRun?.id === sim.id ? 'border-blue-500 bg-blue-50' : ''
                  }`}
                  onClick={() => viewSimulation(sim.id)}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="text-sm font-medium">Run #{sim.id}</div>
                      <div className="text-xs text-gray-500">
                        {new Date(sim.created_at).toLocaleString()}
                      </div>
                      <div className={`text-xs mt-1 ${
                        sim.status === 'completed' ? 'text-green-600' :
                        sim.status === 'failed' ? 'text-red-600' :
                        'text-yellow-600'
                      }`}>
                        {sim.status}
                      </div>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSimulation(sim.id);
                      }}
                      className="text-red-500 text-xs hover:underline"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Selected simulation detail */}
        <div className="lg:col-span-2">
          {selectedRun ? (
            <div className="border rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-2xl font-bold">Simulation #{selectedRun.id}</h2>
                  <p className="text-sm text-gray-500">
                    {new Date(selectedRun.created_at).toLocaleString()}
                  </p>
                  {selectedRun.duration_seconds && (
                    <p className="text-sm text-gray-600">
                      Duration: {selectedRun.duration_seconds.toFixed(1)}s
                    </p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded text-sm ${
                  selectedRun.status === 'completed' ? 'bg-green-100 text-green-800' :
                  selectedRun.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {selectedRun.status}
                </span>
              </div>

              {/* Evaluation Scores */}
              {selectedRun.evaluation && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h3 className="font-semibold text-lg mb-3">Evaluation</h3>
                  <div className="grid grid-cols-3 gap-4 mb-3">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedRun.evaluation.scores.task_completion}/10
                      </div>
                      <div className="text-sm text-gray-600">Task Completion</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {selectedRun.evaluation.scores.naturalness}/10
                      </div>
                      <div className="text-sm text-gray-600">Naturalness</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {selectedRun.evaluation.scores.goal_achieved}/10
                      </div>
                      <div className="text-sm text-gray-600">Goal Achieved</div>
                    </div>
                  </div>
                  <div className="text-center py-2 bg-white rounded border border-gray-200">
                    <div className="text-3xl font-bold text-gray-800">
                      {selectedRun.evaluation.overall_score.toFixed(1)}/10
                    </div>
                    <div className="text-sm text-gray-600">Overall Score</div>
                  </div>
                  {selectedRun.evaluation.feedback && (
                    <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                      <strong>Feedback:</strong> {selectedRun.evaluation.feedback}
                    </div>
                  )}
                </div>
              )}

              {selectedRun.transcript && (
                <div className="space-y-4">
                  {selectedRun.transcript.map((turn, idx) => (
                    <div key={idx} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">
                          {turn.persona || `Agent ${turn.agent}`}
                        </h3>
                        <span className="text-xs text-gray-500">Turn {idx + 1}</span>
                      </div>
                      <p className="text-gray-700 mb-3">{turn.text}</p>
                      {turn.audio && <AudioPlayer audioPath={turn.audio} />}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="border rounded-lg p-6 text-center text-gray-500">
              {simulations.length === 0
                ? 'No simulations yet. Run one to get started!'
                : 'Select a simulation from the list to view details'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
