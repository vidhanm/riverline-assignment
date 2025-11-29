import { useState } from 'react';

export default function EvolutionTree({ versions, onSelectVersion }) {
  const [selectedNode, setSelectedNode] = useState(null);

  // Build tree structure (reverse order so oldest is root)
  const reversedVersions = [...versions].reverse();

  // Calculate tree levels
  const buildTree = () => {
    const tree = [];
    const versionMap = new Map();

    reversedVersions.forEach(v => versionMap.set(v.id, v));

    reversedVersions.forEach((version, idx) => {
      const level = idx; // Simple linear tree for now
      tree.push({
        version,
        level,
        children: versions.filter(v => v.parent_version_id === version.id)
      });
    });

    return tree;
  };

  const tree = buildTree();

  const handleNodeClick = (version) => {
    setSelectedNode(version.id);
    onSelectVersion(version.id);
  };

  return (
    <div className="border rounded-lg p-6 bg-white">
      <h2 className="text-xl font-bold mb-4">Evolution Tree</h2>

      <div className="relative">
        {/* SVG container for lines */}
        <svg className="absolute top-0 left-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
          {tree.map((node, idx) => {
            if (idx === 0) return null; // Root has no parent

            const parentNode = tree.find(t => t.version.id === node.version.parent_version_id);
            if (!parentNode) return null;

            const y1 = idx * 100 + 40; // Node center
            const y2 = tree.indexOf(parentNode) * 100 + 40;
            const x = 150; // Fixed x position

            return (
              <line
                key={`line-${node.version.id}`}
                x1={x}
                y1={y1}
                x2={x}
                y2={y2}
                stroke="#CBD5E0"
                strokeWidth="2"
                strokeDasharray={node.version.fitness_score > parentNode.version.fitness_score ? "0" : "5,5"}
              />
            );
          })}
        </svg>

        {/* Nodes */}
        <div className="relative space-y-4" style={{ zIndex: 1 }}>
          {tree.map((node, idx) => {
            const { version } = node;
            const improvement = idx > 0
              ? version.fitness_score - tree[idx - 1].version.fitness_score
              : 0;

            return (
              <div
                key={version.id}
                className="flex items-center gap-4"
                style={{ paddingLeft: `${node.level * 20}px` }}
              >
                {/* Node */}
                <div
                  onClick={() => handleNodeClick(version)}
                  className={`
                    relative border-2 rounded-lg p-4 cursor-pointer transition-all
                    ${selectedNode === version.id
                      ? 'border-blue-500 bg-blue-50 shadow-lg'
                      : 'border-gray-300 bg-white hover:border-blue-400 hover:shadow-md'
                    }
                    ${idx === tree.length - 1 ? 'border-green-500' : ''}
                  `}
                  style={{ width: '300px' }}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-bold text-lg">
                        Version {version.version}
                        {idx === tree.length - 1 && (
                          <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                            ACTIVE
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(version.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-blue-600">
                        {version.fitness_score.toFixed(1)}
                      </div>
                      <div className="text-xs text-gray-500">/ 10</div>
                    </div>
                  </div>

                  {idx > 0 && (
                    <div className={`text-xs font-medium ${
                      improvement > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {improvement > 0 ? '↑' : '↓'} {improvement > 0 ? '+' : ''}{improvement.toFixed(1)}
                      {' from v' + tree[idx - 1].version.version}
                    </div>
                  )}

                  {version.baseline_score && (
                    <div className="mt-2 text-xs text-gray-600">
                      Baseline: {version.baseline_score.toFixed(1)} / 10
                    </div>
                  )}

                  {/* Mutation count badge */}
                  {version.mutation_attempts && version.mutation_attempts.length > 0 && (
                    <div className="mt-2 flex gap-1">
                      {version.mutation_attempts.map((mut) => (
                        <div
                          key={mut.mutation_index}
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                            mut.is_winner
                              ? 'bg-yellow-400 text-yellow-900 font-bold'
                              : 'bg-gray-200 text-gray-600'
                          }`}
                          title={`Mutation ${mut.mutation_index}: ${mut.avg_score?.toFixed(1)}/10`}
                        >
                          {mut.mutation_index}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded text-xs text-gray-600">
        <div className="font-semibold mb-2">Legend:</div>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-gray-400"></div>
            <span>Solid line: Improvement</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-gray-400" style={{ backgroundImage: 'repeating-linear-gradient(to right, #CBD5E0 0, #CBD5E0 3px, transparent 3px, transparent 6px)' }}></div>
            <span>Dashed line: No improvement / regression</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-yellow-400"></div>
            <span>Yellow circle: Winning mutation</span>
          </div>
        </div>
      </div>
    </div>
  );
}
