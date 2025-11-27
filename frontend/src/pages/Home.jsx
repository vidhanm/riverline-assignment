import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Voice AI Sandbox</h1>
      <p className="text-gray-600 mb-8">
        Simulate conversations between AI personas with voice generation and evolution capabilities
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link
          to="/personas"
          className="p-6 border rounded-lg hover:shadow-lg transition"
        >
          <h2 className="text-2xl font-semibold mb-2">Personas</h2>
          <p className="text-gray-600">Manage AI personalities</p>
        </Link>

        <Link
          to="/scenarios"
          className="p-6 border rounded-lg hover:shadow-lg transition"
        >
          <h2 className="text-2xl font-semibold mb-2">Scenarios</h2>
          <p className="text-gray-600">Define conversation scenarios</p>
        </Link>

        <Link
          to="/simulations"
          className="p-6 border rounded-lg hover:shadow-lg transition"
        >
          <h2 className="text-2xl font-semibold mb-2">Simulations</h2>
          <p className="text-gray-600">View conversation history</p>
        </Link>

        <Link
          to="/evolution"
          className="p-6 border rounded-lg hover:shadow-lg transition"
        >
          <h2 className="text-2xl font-semibold mb-2">Evolution</h2>
          <p className="text-gray-600">Self-improving AI agents</p>
        </Link>
      </div>
    </div>
  );
}
