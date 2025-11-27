import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

export default function Evolution() {
  const [personas, setPersonas] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState('');
  const [selectedScenario, setSelectedScenario] = useState('');
  const [loading, setLoading] = useState(false);
  const [evolutionResult, setEvolutionResult] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersions, setSelectedVersions] = useState([null, null]); // For comparison
  const [compareView, setCompareView] = useState(0); // 0 = version 1, 1 = version 2

  useEffect(() => {
    fetchPersonas();
    fetchScenarios();
  }, []);

  useEffect(() => {
    if (selectedPersona) {
      fetchVersions();
    }
  }, [selectedPersona]);

  const fetchPersonas = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/personas/`);
      setPersonas(response.data);
    } catch (error) {
      console.error('Error fetching personas:', error);
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

  const fetchVersions = async () => {
    if (!selectedPersona) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/evolve/versions/${selectedPersona}`);
      setVersions(response.data.versions);
    } catch (error) {
      console.error('Error fetching versions:', error);
    }
  };

  const runEvolution = async () => {
    if (!selectedPersona || !selectedScenario) {
      alert('Please select both persona and scenario');
      return;
    }

    setLoading(true);
    setEvolutionResult(null);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/evolve/${selectedPersona}?scenario_id=${selectedScenario}`
      );
      setEvolutionResult(response.data);
      fetchVersions(); // Refresh version list
    } catch (error) {
      console.error('Error running evolution:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const activateVersion = async (versionId) => {
    if (!confirm('Activate this version? It will become the current persona prompt.')) return;

    try {
      await axios.post(`${API_BASE_URL}/evolve/versions/${versionId}/activate`);
      alert('Version activated successfully!');
      fetchVersions(); // Refresh to show updated active status
    } catch (error) {
      console.error('Error activating version:', error);
      alert('Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getVersionPrompt = (versionId) => {
    const version = versions.find(v => v.id === versionId);
    return version?.system_prompt || '';
  };

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Evolution Lab</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          {/* Evolution Controls */}
          <div className="border rounded-lg p-4 bg-gray-50">
            <h2 className="font-semibold mb-3">Run Evolution</h2>

            <div className="space-y-3">
              <div>
                <label className="text-sm text-gray-600 block mb-1">Persona</label>
                <select
                  value={selectedPersona}
                  onChange={(e) => setSelectedPersona(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select persona...</option>
                  {personas.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-sm text-gray-600 block mb-1">Scenario</label>
                <select
                  value={selectedScenario}
                  onChange={(e) => setSelectedScenario(e.target.value)}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select scenario...</option>
                  {scenarios.map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>

              <button
                onClick={runEvolution}
                disabled={loading}
                className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
              >
                {loading ? 'Evolving... (~8 min)' : 'Evolve Now'}
              </button>
            </div>

            {loading && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
                Evolution running... This takes about 8 minutes (14 simulations).
              </div>
            )}
          </div>

          {/* Version History */}
          {selectedPersona && (
            <div className="border rounded-lg p-4">
              <h2 className="font-semibold mb-3">Version History</h2>

              {versions.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  No versions yet. Run evolution to create first version.
                </p>
              ) : (
                <div className="space-y-2 max-h-[500px] overflow-y-auto">
                  {versions.map((version, idx) => {
                    const prevVersion = versions[idx + 1];
                    const improvement = prevVersion
                      ? (version.fitness_score - prevVersion.fitness_score).toFixed(1)
                      : null;

                    return (
                      <div
                        key={version.id}
                        className="border rounded-lg p-3 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <div className="font-medium">
                              Version {version.version}
                              {idx === 0 && (
                                <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                  ACTIVE
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">
                              {new Date(version.created_at).toLocaleDateString()}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold text-blue-600">
                              {version.fitness_score.toFixed(1)}/10
                            </div>
                          </div>
                        </div>

                        {improvement && (
                          <div className={`text-xs mb-2 ${
                            parseFloat(improvement) > 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            ↑ {improvement > 0 ? '+' : ''}{improvement} from v{version.version - 1}
                          </div>
                        )}

                        <div className="flex gap-2">
                          {idx !== 0 && (
                            <button
                              onClick={() => activateVersion(version.id)}
                              className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                            >
                              Activate
                            </button>
                          )}
                          <button
                            onClick={() => setSelectedVersions([version.id, null])}
                            className="text-xs px-2 py-1 border rounded hover:bg-gray-100"
                          >
                            View Prompt
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* Evolution Results */}
          {evolutionResult && (
            <div className="border rounded-lg p-6 mb-6">
              {evolutionResult.evolved ? (
                <>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-4 text-center">
                    <h2 className="text-2xl font-bold text-green-800 mb-4">
                      EVOLUTION COMPLETE! ✅
                    </h2>
                    <div className="text-4xl font-bold mb-2">
                      <span className="text-gray-600">{evolutionResult.baseline_score.toFixed(1)}</span>
                      <span className="text-gray-400 mx-3">→</span>
                      <span className="text-green-600">{evolutionResult.new_score.toFixed(1)}</span>
                      <span className="text-gray-500">/10</span>
                    </div>
                    <div className="text-lg text-green-700 mb-3">
                      +{evolutionResult.improvement.toFixed(1)} improvement 🎯
                    </div>
                    <div className="text-sm text-gray-600">
                      New version saved: v{evolutionResult.new_version}
                    </div>
                  </div>

                  <div className="bg-gray-50 border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">Mutation Results</h3>
                    <div className="space-y-2">
                      {evolutionResult.mutation_scores.map((mut) => (
                        <div
                          key={mut.mutation_id}
                          className={`p-3 border rounded ${
                            mut.avg_score === evolutionResult.new_score
                              ? 'bg-green-50 border-green-300'
                              : 'bg-white'
                          }`}
                        >
                          <div className="flex justify-between items-center">
                            <span className="font-medium">
                              Mutation {mut.mutation_id + 1}
                              {mut.avg_score === evolutionResult.new_score && (
                                <span className="ml-2 text-yellow-600">⭐ WINNER</span>
                              )}
                            </span>
                            <span className="text-lg font-bold text-blue-600">
                              {mut.avg_score.toFixed(1)}/10
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                  <h2 className="text-xl font-bold text-yellow-800 mb-2">
                    No Evolution Needed
                  </h2>
                  <p className="text-gray-700">
                    {evolutionResult.reason === 'Score above threshold'
                      ? `Baseline score (${evolutionResult.baseline_score.toFixed(1)}/10) is above threshold (${evolutionResult.threshold})`
                      : 'No improvement found in mutations'}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Prompt Comparison */}
          {selectedVersions[0] && (
            <div className="border rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Prompt Viewer</h2>

              <div className="bg-gray-50 border rounded-lg p-4">
                <div className="mb-3">
                  <label className="text-sm text-gray-600 block mb-1">Select Version</label>
                  <select
                    value={selectedVersions[0] || ''}
                    onChange={(e) => setSelectedVersions([parseInt(e.target.value), null])}
                    className="w-full border rounded px-3 py-2"
                  >
                    {versions.map((v) => (
                      <option key={v.id} value={v.id}>
                        Version {v.version} - {v.fitness_score.toFixed(1)}/10
                      </option>
                    ))}
                  </select>
                </div>

                <div className="bg-white border rounded p-4">
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {getVersionPrompt(selectedVersions[0])}
                  </pre>
                </div>

                <div className="mt-3 text-sm text-gray-600">
                  <strong>Fitness Score:</strong>{' '}
                  {versions.find(v => v.id === selectedVersions[0])?.fitness_score.toFixed(1)}/10
                </div>
              </div>
            </div>
          )}

          {/* Empty State */}
          {!evolutionResult && !selectedVersions[0] && (
            <div className="border rounded-lg p-6 text-center text-gray-500">
              {!selectedPersona
                ? 'Select a persona to view version history'
                : versions.length === 0
                ? 'No versions yet. Run evolution to create your first version!'
                : 'Run evolution or select a version to view details'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
