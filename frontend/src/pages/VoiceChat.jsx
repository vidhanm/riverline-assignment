import { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

// LiveKit imports
import {
  LiveKitRoom,
  useVoiceAssistant,
  RoomAudioRenderer,
  useTranscriptions,
} from '@livekit/components-react';
import '@livekit/components-styles';

function VoiceChat() {
  const [status, setStatus] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [connectionInfo, setConnectionInfo] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);

  // Check voice system status
  useEffect(() => {
    checkStatus();
    fetchPersonas();
  }, []);

  const checkStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/voice/status`);
      setStatus(response.data);
    } catch (err) {
      setError('Failed to check voice status');
    }
  };

  const fetchPersonas = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/voice/personas`);
      setPersonas(response.data.personas);
      if (response.data.personas.length > 0) {
        setSelectedPersona(response.data.personas[0]);
      }
    } catch (err) {
      console.error('Failed to fetch personas:', err);
    }
  };

  const startVoiceChat = async () => {
    setIsConnecting(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/voice/token`, {
        room_name: `debt-collection-${Date.now()}`,
        participant_name: 'customer',
        persona_id: selectedPersona?.id || null,
      });

      setConnectionInfo(response.data);
      setIsConnected(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start voice chat');
    } finally {
      setIsConnecting(false);
    }
  };

  const endVoiceChat = () => {
    setConnectionInfo(null);
    setIsConnected(false);
  };

  // Not configured state
  if (status && !status.available) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">🎙️ Voice Chat</h1>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-yellow-800 mb-4">
            ⚠️ Voice System Not Configured
          </h2>
          <p className="text-yellow-700 mb-4">{status.message}</p>
          
          <div className="bg-white rounded p-4 mt-4">
            <h3 className="font-semibold mb-2">Setup Instructions:</h3>
            <ol className="list-decimal list-inside space-y-2 text-sm">
              <li>
                <strong>Get LiveKit Cloud credentials from:</strong>
                <a href="https://cloud.livekit.io" className="text-blue-600 ml-2">cloud.livekit.io</a>
              </li>
              <li>
                <strong>Add to backend/.env:</strong>
                <pre className="bg-gray-100 p-2 mt-2 rounded text-xs">
{`LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret`}
                </pre>
              </li>
              <li>
                <strong>Start the voice agent:</strong>
                <code className="bg-gray-100 px-2 py-1 ml-2 rounded">
                  python voice_agent.py dev
                </code>
              </li>
            </ol>
          </div>
          
          <div className="mt-4 flex gap-2">
            <span className={`px-2 py-1 rounded text-sm ${status.livekit_configured ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              LiveKit: {status.livekit_configured ? '✓' : '✗'}
            </span>
            <span className={`px-2 py-1 rounded text-sm ${status.deepgram_configured ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              Deepgram: {status.deepgram_configured ? '✓' : '✗'}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Connected state - show LiveKit room
  if (isConnected && connectionInfo) {
    return (
      <LiveKitRoom
        token={connectionInfo.token}
        serverUrl={connectionInfo.url}
        connect={true}
        audio={true}
        video={false}
        onDisconnected={endVoiceChat}
      >
        <VoiceChatInterface 
          persona={selectedPersona}
          onEnd={endVoiceChat}
        />
        <RoomAudioRenderer />
      </LiveKitRoom>
    );
  }

  // Default state - setup/start
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">🎙️ Voice Chat</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Talk to the Evolved Agent</h2>
        <p className="text-gray-600 mb-6">
          Have a real voice conversation with the debt collection agent. 
          The agent uses the evolved prompt from the DGM evolution system.
        </p>

        {/* Persona Selection */}
        {personas.length > 0 && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Agent Persona:
            </label>
            <select
              value={selectedPersona?.id || ''}
              onChange={(e) => {
                const persona = personas.find(p => p.id === parseInt(e.target.value));
                setSelectedPersona(persona);
              }}
              className="w-full border rounded-lg px-3 py-2"
            >
              {personas.map(persona => (
                <option key={persona.id} value={persona.id}>
                  {persona.name} 
                  {persona.has_evolved && ` (v${persona.version} - Score: ${persona.fitness_score?.toFixed(1)})`}
                </option>
              ))}
            </select>
            
            {selectedPersona?.has_evolved && (
              <p className="text-sm text-green-600 mt-2">
                ✓ Using evolved version {selectedPersona.version} with fitness score {selectedPersona.fitness_score?.toFixed(1)}/10
              </p>
            )}
          </div>
        )}

        {/* Status indicators */}
        {status && (
          <div className="flex gap-2 mb-6">
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
              ✓ LiveKit Ready
            </span>
            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
              ✓ Voice Ready
            </span>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Start button */}
        <button
          onClick={startVoiceChat}
          disabled={isConnecting}
          className={`w-full py-4 rounded-lg text-white text-lg font-semibold transition
            ${isConnecting 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-blue-500 hover:bg-blue-600'
            }`}
        >
          {isConnecting ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Connecting...
            </span>
          ) : (
            '🎤 Start Voice Chat'
          )}
        </button>
      </div>

      {/* Instructions */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="font-semibold mb-3">How it works:</h3>
        <ol className="list-decimal list-inside space-y-2 text-gray-600">
          <li>Click "Start Voice Chat" to connect</li>
          <li>Allow microphone access when prompted</li>
          <li>Click the mic button to speak, click again when done</li>
          <li>The agent will respond after you finish</li>
          <li>Speak in Hindi for best results</li>
        </ol>
      </div>
    </div>
  );
}


// Main Voice Chat Interface Component - Push to Talk Style
function VoiceChatInterface({ persona, onEnd }) {
  const { state, agentTranscriptions } = useVoiceAssistant();
  const transcriptions = useTranscriptions();
  const [isMicOn, setIsMicOn] = useState(false);
  const [currentTurn, setCurrentTurn] = useState('agent'); // 'user' or 'agent'

  // Process transcriptions into messages format
  // Agent identity typically contains 'agent' or is not 'customer'
  const messages = transcriptions.map((t, idx) => {
    const participantId = t.participant?.identity || '';
    // User is 'customer', agent is anything else (usually contains 'agent' or is the agent participant)
    const isUser = participantId === 'customer';
    
    return {
      id: idx,
      text: t.text || t.segment?.text || '',
      isUser: isUser,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      participant: participantId, // for debugging
    };
  }).filter(m => m.text.trim() !== '');

  // Toggle microphone
  const toggleMic = () => {
    if (isMicOn) {
      // User finished speaking, agent's turn
      setIsMicOn(false);
      setCurrentTurn('agent');
    } else {
      // User wants to speak
      setIsMicOn(true);
      setCurrentTurn('user');
    }
  };

  // Get status based on current turn and mic state
  const getStatusInfo = () => {
    if (isMicOn) {
      return { 
        text: 'Your turn - Speak now...', 
        subtext: 'Click mic when done',
        color: 'text-green-400' 
      };
    } else if (currentTurn === 'agent') {
      return { 
        text: "Agent's turn", 
        subtext: 'Click mic to respond',
        color: 'text-blue-400' 
      };
    }
    return { 
      text: 'Ready', 
      subtext: 'Click mic to start',
      color: 'text-gray-400' 
    };
  };

  const statusInfo = getStatusInfo();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex flex-col">
      {/* Header */}
      <div className="text-center py-6">
        <h1 className="text-2xl font-bold text-white">🎙️ Voice Chat</h1>
        <p className="text-gray-400 text-sm">Speaking with {persona?.name || 'Marcus'}</p>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex">
        {/* Left Panel - Agent & Controls */}
        <div className="flex-1 flex flex-col items-center justify-center px-8">
          
          {/* Agent Info */}
          <div className="text-center mb-8">
            <div className="w-24 h-24 bg-slate-700 rounded-full flex items-center justify-center text-5xl mb-4 mx-auto border-2 border-slate-600">
              🎙️
            </div>
            <h2 className="text-2xl font-bold text-white">
              {persona?.name || 'Marcus'}
            </h2>
            <p className="text-gray-400">Debt Collection Agent</p>
            {persona?.has_evolved && (
              <span className="inline-block mt-2 bg-green-900/50 text-green-400 px-3 py-1 rounded-full text-xs">
                Evolved v{persona.version} • Score: {persona.fitness_score?.toFixed(1)}/10
              </span>
            )}
          </div>

          {/* Main Mic Button */}
          <div className="relative mb-8">
            {/* Pulsing rings when mic is on */}
            {isMicOn && (
              <>
                <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-20" 
                     style={{ animationDuration: '1s' }} />
                <div className="absolute inset-2 bg-green-500 rounded-full animate-ping opacity-30" 
                     style={{ animationDuration: '1s', animationDelay: '0.3s' }} />
              </>
            )}
            
            {/* Mic Button */}
            <button
              onClick={toggleMic}
              className={`
                relative z-10 w-32 h-32 rounded-full flex items-center justify-center
                text-5xl transition-all duration-300 transform
                ${isMicOn 
                  ? 'bg-green-500 hover:bg-green-600 scale-110 shadow-lg shadow-green-500/50' 
                  : 'bg-slate-700 hover:bg-slate-600 border-4 border-slate-600 hover:border-blue-500'
                }
              `}
            >
              {isMicOn ? '🎤' : '🎙️'}
            </button>
          </div>

          {/* Status Text */}
          <div className="text-center mb-6">
            <p className={`text-xl font-semibold ${statusInfo.color}`}>
              {statusInfo.text}
            </p>
            <p className="text-gray-500 text-sm mt-1">
              {statusInfo.subtext}
            </p>
          </div>

          {/* Turn Indicator */}
          <div className="flex items-center gap-8 mb-8">
            <div className={`text-center transition-all ${isMicOn ? 'opacity-100 scale-110' : 'opacity-50'}`}>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl
                ${isMicOn ? 'bg-green-500' : 'bg-slate-700'}`}>
                👤
              </div>
              <p className="text-xs text-gray-400 mt-1">You</p>
            </div>
            
            <div className="text-2xl text-gray-600">⟷</div>
            
            <div className={`text-center transition-all ${!isMicOn ? 'opacity-100 scale-110' : 'opacity-50'}`}>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl
                ${!isMicOn ? 'bg-blue-500' : 'bg-slate-700'}`}>
                🤖
              </div>
              <p className="text-xs text-gray-400 mt-1">Agent</p>
            </div>
          </div>

          {/* End Call Button */}
          <button
            onClick={onEnd}
            className="bg-red-500/20 hover:bg-red-500 text-red-400 hover:text-white 
                       px-6 py-2 rounded-full font-medium transition-all duration-300
                       border border-red-500/50 hover:border-red-500
                       flex items-center gap-2"
          >
            <span>📞</span>
            <span>End Call</span>
          </button>
        </div>

        {/* Right Panel - Transcript */}
        <div className="w-96 bg-white/5 backdrop-blur border-l border-slate-700 flex flex-col">
          {/* Transcript Header */}
          <div className="px-4 py-3 border-b border-slate-700 bg-slate-800/50">
            <h3 className="font-semibold text-white flex items-center gap-2">
              💬 Conversation
            </h3>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-12">
                <p className="text-4xl mb-3">💬</p>
                <p>Conversation will appear here</p>
                <p className="text-sm mt-1">Click the mic to start speaking</p>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div 
                  key={idx}
                  className={`mb-3 ${msg.isUser ? 'text-right' : 'text-left'}`}
                >
                  <div className={`
                    inline-block max-w-[85%] px-4 py-2 rounded-2xl
                    ${msg.isUser 
                      ? 'bg-blue-500 text-white rounded-br-md' 
                      : 'bg-slate-700 text-gray-200 rounded-bl-md'
                    }
                  `}>
                    <p className="text-sm">{msg.text}</p>
                  </div>
                  <p className="text-xs text-gray-600 mt-1 px-2">
                    {msg.timestamp}
                  </p>
                </div>
              ))
            )}
          </div>

          {/* Tip */}
          <div className="p-3 border-t border-slate-700 bg-slate-800/30">
            <p className="text-xs text-gray-500 text-center">
              💡 Speak in Hindi for best results
            </p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="text-center py-3 border-t border-slate-800">
        <p className="text-gray-600 text-xs">
          Connected via LiveKit • Sarvam AI Voice
        </p>
      </div>
    </div>
  );
}


export default VoiceChat;
