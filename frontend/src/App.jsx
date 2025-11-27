import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import Personas from './pages/Personas';
import Scenarios from './pages/Scenarios';
import Simulations from './pages/Simulations';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Link to="/" className="text-xl font-bold">Voice AI Sandbox</Link>
              <div className="flex gap-6">
                <Link to="/" className="hover:text-blue-500">Home</Link>
                <Link to="/personas" className="hover:text-blue-500">Personas</Link>
                <Link to="/scenarios" className="hover:text-blue-500">Scenarios</Link>
                <Link to="/simulations" className="hover:text-blue-500">Simulations</Link>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/personas" element={<Personas />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/simulations" element={<Simulations />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
