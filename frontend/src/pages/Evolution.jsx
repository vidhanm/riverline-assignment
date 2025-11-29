import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
import EvolutionTree from '../components/EvolutionTree';
import MutationDetails from '../components/MutationDetails';

export default function Evolution() {
  const [personas, setPersonas] = useState([]);
  const [scenarios, setScenarios] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState('');
  const [selectedScenarios, setSelectedScenarios] = useState([]);  // Changed to array
  const [loading, setLoading] = useState(false);
  const [evolutionResult, setEvolutionResult] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersions, setSelectedVersions] = useState([null, null]); // For comparison
  const [compareView, setCompareView] = useState(0); // 0 = version 1, 1 = version 2
  const [viewMode, setViewMode] = useState('tree'); // 'tree' or 'list'
  const [selectedMutation, setSelectedMutation] = useState(null);

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
    if (!selectedPersona || selectedScenarios.length === 0) {
      alert('Please select persona and at least one scenario');
      return;
    }

    setLoading(true);
    setEvolutionResult(null);

    try {
      const scenarioIdsParam = selectedScenarios.join(',');  // Join with commas
      const response = await axios.post(
        `${API_BASE_URL}/evolve/${selectedPersona}?scenario_ids=${scenarioIdsParam}`
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
                <label className="text-sm text-gray-600 block mb-1">
                  Scenarios (select multiple)
                </label>
                <div className="space-y-2 max-h-48 overflow-y-auto border rounded p-3 bg-white">
                  {scenarios.length === 0 ? (
                    <p className="text-xs text-gray-500 text-center py-2">No scenarios available</p>
                  ) : (
                    scenarios.map((s) => (
                      <label key={s.id} className="flex items-start gap-2 cursor-pointer hover:bg-gray-50 p-1 rounded">
                        <input
                          type="checkbox"
                          checked={selectedScenarios.includes(s.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedScenarios([...selectedScenarios, s.id]);
                            } else {
                              setSelectedScenarios(selectedScenarios.filter(id => id !== s.id));
                            }
                          }}
                          className="mt-1"
                        />
                        <span className="text-sm flex-1">{s.name}</span>
                      </label>
                    ))
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {selectedScenarios.length} scenario{selectedScenarios.length !== 1 ? 's' : ''} selected
                </p>
              </div>

              <button
                onClick={runEvolution}
                disabled={loading || selectedScenarios.length === 0}
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

          {/* View Mode Toggle */}
          {selectedPersona && versions.length > 0 && (
            <div className="border rounded-lg p-3 bg-gray-50">
              <label className="text-sm text-gray-600 block mb-2">View Mode</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setViewMode('tree')}
                  className={`flex-1 px-3 py-2 rounded text-sm ${
                    viewMode === 'tree'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white border hover:bg-gray-100'
                  }`}
                >
                  🌳 Tree
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`flex-1 px-3 py-2 rounded text-sm ${
                    viewMode === 'list'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white border hover:bg-gray-100'
                  }`}
                >
                  📋 List
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Evolution Tree or Mutation Details */}
          {selectedPersona && versions.length > 0 && (
            <>
              {viewMode === 'tree' ? (
                <EvolutionTree
                  versions={versions}
                  onSelectVersion={(versionId) => {
                    const version = versions.find(v => v.id === versionId);
                    setSelectedVersions([versionId, null]);
                    // Show first mutation by default
                    if (version?.mutation_attempts?.length > 0) {
                      setSelectedMutation(version.mutation_attempts[0]);
                    }
                  }}
                />
              ) : (
                <div className="border rounded-lg p-4">
                  <h2 className="font-semibold mb-3">Version List</h2>
                  <div className="space-y-2">
                    {versions.map((version, idx) => (
                      <div
                        key={version.id}
                        onClick={() => {
                          setSelectedVersions([version.id, null]);
                          if (version.mutation_attempts?.length > 0) {
                            setSelectedMutation(version.mutation_attempts[0]);
                          }
                        }}
                        className="border rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <span className="font-medium">Version {version.version}</span>
                            {idx === 0 && (
                              <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                                ACTIVE
                              </span>
                            )}
                          </div>
                          <span className="text-xl font-bold text-blue-600">
                            {version.fitness_score.toFixed(1)}/10
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Mutation Details Panel */}
              {selectedVersions[0] && (
                <div className="border rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold">Evolution Reasoning</h2>
                    {versions.find(v => v.id === selectedVersions[0])?.mutation_attempts?.length > 0 && (
                      <div className="flex gap-2">
                        {versions.find(v => v.id === selectedVersions[0]).mutation_attempts.map((mut) => (
                          <button
                            key={mut.mutation_index}
                            onClick={() => setSelectedMutation(mut)}
                            className={`px-3 py-1 rounded text-sm ${
                              selectedMutation?.mutation_index === mut.mutation_index
                                ? 'bg-blue-500 text-white'
                                : 'border hover:bg-gray-100'
                            }`}
                          >
                            Mutation {mut.mutation_index}
                            {mut.is_winner && ' ⭐'}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <MutationDetails
                    mutation={selectedMutation}
                    versionNumber={versions.find(v => v.id === selectedVersions[0])?.version}
                  />
                </div>
              )}
            </>
          )}

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
