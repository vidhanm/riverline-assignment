import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-4xl font-bold mb-8">Voice AI Sandbox</h1>
      <p className="text-gray-600 mb-8">
        Simulate conversations between AI personas with voice generation and evolution capabilities
      </p>

      {/* Voice Chat Hero Card */}
      <Link
        to="/voice"
        className="block p-8 mb-8 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg hover:shadow-xl transition text-white"
      >
        <div className="flex items-center gap-4">
          <span className="text-5xl">🎙️</span>
          <div>
            <h2 className="text-3xl font-bold mb-2">Voice Chat</h2>
            <p className="text-green-100">Talk to the evolved debt collection agent in real-time</p>
          </div>
        </div>
      </Link>

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
