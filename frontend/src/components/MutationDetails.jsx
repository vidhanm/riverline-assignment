export default function MutationDetails({ mutation, versionNumber }) {
  if (!mutation) {
    return (
      <div className="text-center text-gray-500 py-8">
        Select a mutation to view reasoning details
      </div>
    );
  }

  const metadata = mutation.mutation_metadata || {};

  return (
    <div className="space-y-4">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-bold text-lg mb-2">
          Version {versionNumber} - Mutation {mutation.mutation_index}
          {mutation.is_winner && <span className="ml-2 text-yellow-600">⭐ WINNER</span>}
        </h3>
        <div className="text-sm text-gray-700">
          <span className="font-semibold">Score:</span> {mutation.avg_score?.toFixed(1) || 'N/A'}/10
        </div>
      </div>

      {/* Metadata summary */}
      {metadata.avg_scores && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-3">Performance Metrics</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-gray-50 rounded p-3">
              <div className="text-xs text-gray-600 mb-1">Task Completion</div>
              <div className="text-2xl font-bold text-blue-600">
                {metadata.avg_scores.task_completion?.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <div className="text-xs text-gray-600 mb-1">Naturalness</div>
              <div className="text-2xl font-bold text-blue-600">
                {metadata.avg_scores.naturalness?.toFixed(1)}
              </div>
            </div>
            <div className="bg-gray-50 rounded p-3">
              <div className="text-xs text-gray-600 mb-1">Goal Achieved</div>
              <div className="text-2xl font-bold text-blue-600">
                {metadata.avg_scores.goal_achieved?.toFixed(1)}
              </div>
            </div>
          </div>
          <div className="mt-3 text-center">
            <div className="text-xs text-gray-600">Overall Average</div>
            <div className="text-3xl font-bold text-indigo-600">
              {metadata.overall_avg?.toFixed(1)}/10
            </div>
          </div>
        </div>
      )}

      {/* Scenarios tested */}
      {metadata.scenarios_tested && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2">Tested Across {metadata.num_evaluations} Simulations</h4>
          <div className="flex flex-wrap gap-2">
            {metadata.scenarios_tested.map((scenario, idx) => (
              <span
                key={idx}
                className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm"
              >
                {scenario}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Feedback */}
      {metadata.feedback_used && metadata.feedback_used.length > 0 && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2">Evaluator Feedback</h4>
          <div className="space-y-2">
            {metadata.feedback_used.map((feedback, idx) => (
              <div key={idx} className="bg-yellow-50 border-l-4 border-yellow-400 p-3 text-sm">
                {feedback}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Success examples */}
      {metadata.success_examples && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2 text-green-700">✅ Success Examples (Learning From)</h4>
          <div className="bg-green-50 border border-green-200 rounded p-3">
            <pre className="text-xs whitespace-pre-wrap text-gray-700">
              {metadata.success_examples}
            </pre>
          </div>
        </div>
      )}

      {/* Failure examples */}
      {metadata.failure_examples && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2 text-red-700">❌ Failure Examples (Avoiding)</h4>
          <div className="bg-red-50 border border-red-200 rounded p-3">
            <pre className="text-xs whitespace-pre-wrap text-gray-700">
              {metadata.failure_examples}
            </pre>
          </div>
        </div>
      )}

      {/* Full reasoning prompt */}
      {mutation.reasoning_prompt && (
        <details className="border rounded-lg p-4">
          <summary className="font-semibold cursor-pointer hover:text-blue-600">
            🧠 Full Reasoning Prompt (Click to expand)
          </summary>
          <div className="mt-3 bg-gray-50 rounded p-4">
            <pre className="text-xs whitespace-pre-wrap text-gray-700">
              {mutation.reasoning_prompt}
            </pre>
          </div>
        </details>
      )}

      {/* Mutated prompt */}
      <div className="border rounded-lg p-4">
        <h4 className="font-semibold mb-2">📝 Generated Prompt</h4>
        <div className="bg-blue-50 border border-blue-200 rounded p-4">
          <pre className="text-sm whitespace-pre-wrap text-gray-800">
            {mutation.mutated_prompt}
          </pre>
        </div>
      </div>
    </div>
  );
}
