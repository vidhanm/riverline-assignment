import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';

// LiveKit imports
import {
  LiveKitRoom,
  useVoiceAssistant,
  RoomAudioRenderer,
  useTranscriptions,
  useTrackToggle,
} from '@livekit/components-react';
import { Track } from 'livekit-client';
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


// Main Voice Chat Interface Component - Clean & Focused
function VoiceChatInterface({ persona, onEnd }) {
  const { state } = useVoiceAssistant();
  const transcriptions = useTranscriptions();
  const messagesEndRef = useRef(null);

  // Real microphone control via LiveKit - starts MUTED
  const { toggle: toggleMic, enabled: isMicOn, pending: isMicPending } = useTrackToggle({
    source: Track.Source.Microphone,
    initialState: false, // Start with mic OFF - user must click to speak
  });

  // DEBUG: Remove after testing
  // useEffect(() => {
  //   if (transcriptions.length > 0) {
  //     console.log('=== TRANSCRIPTIONS DEBUG ===');
  //     transcriptions.forEach((t, idx) => {
  //       console.log(`[${idx}] participantInfo:`, t.participantInfo);
  //     });
  //   }
  // }, [transcriptions]);

  // Process transcriptions into messages
  // Agent has identity like "agent-xxx", User has identity "customer"
  const messages = transcriptions.map((t, idx) => {
    const identity = t.participantInfo?.identity || '';
    const isUser = identity === 'customer';
    return {
      id: idx,
      text: t.text || '',
      isUser,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };
  }).filter(m => m.text.trim() !== '');

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-screen bg-slate-900 flex">
      {/* Left Panel - Controls */}
      <div className="flex-1 flex flex-col items-center justify-center relative">
        
        {/* End Call - Top Right Corner */}
        <button
          onClick={onEnd}
          className="absolute top-4 right-4 text-red-400 hover:text-red-300 hover:bg-red-500/10 
                     px-4 py-2 rounded-lg transition-all text-sm flex items-center gap-2"
        >
          <span>✕</span>
          <span>End</span>
        </button>

        {/* Agent Name - Compact */}
        <div className="text-center mb-10">
          <h2 className="text-xl font-semibold text-white">{persona?.name || 'Marcus'}</h2>
          <p className="text-slate-500 text-sm">Debt Collection Agent</p>
        </div>

        {/* Hero Mic Button - Controls REAL microphone */}
        <button
          onClick={() => toggleMic()}
          disabled={isMicPending}
          className={`
            relative w-40 h-40 rounded-full flex flex-col items-center justify-center
            transition-all duration-300 transform cursor-pointer
            ${isMicPending ? 'opacity-50 cursor-wait' : ''}
            ${isMicOn 
              ? 'bg-gradient-to-br from-red-500 to-red-600 scale-105 shadow-2xl shadow-red-500/40' 
              : 'bg-slate-800 hover:bg-slate-700 border-2 border-slate-600 hover:border-slate-500'
            }
          `}
        >
          {/* Pulse animation when active - RED for recording */}
          {isMicOn && (
            <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-20" />
          )}
          
          {/* Icon */}
          <span className="text-5xl relative z-10 mb-1">
            {isMicOn ? '🎤' : '🎙️'}
          </span>
          
          {/* Label inside button */}
          <span className={`text-xs font-medium relative z-10 ${isMicOn ? 'text-white' : 'text-slate-400'}`}>
            {isMicPending ? 'Starting...' : (isMicOn ? 'Tap to mute' : 'Tap to speak')}
          </span>
        </button>

        {/* Status - Single Line */}
        <div className="mt-8 text-center">
          <p className={`text-lg font-medium ${isMicOn ? 'text-red-400' : 'text-slate-400'}`}>
            {isMicOn ? '🔴 LIVE - Listening...' : '🎙️ Mic muted'}
          </p>
        </div>

        {/* Connection status - subtle footer */}
        <p className="absolute bottom-4 text-slate-600 text-xs">
          LiveKit • Sarvam AI
        </p>
      </div>

      {/* Right Panel - Conversation */}
      <div className="w-[380px] bg-slate-800/50 border-l border-slate-700/50 flex flex-col">
        
        {/* Header */}
        <div className="px-5 py-4 border-b border-slate-700/50">
          <h3 className="font-medium text-white">Conversation</h3>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
              <p className="text-3xl mb-3">💬</p>
              <p className="text-sm">Start speaking to begin</p>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${msg.isUser ? 'order-2' : 'order-1'}`}>
                    {/* Speaker label */}
                    <p className={`text-xs mb-1 ${msg.isUser ? 'text-right text-slate-500' : 'text-slate-500'}`}>
                      {msg.isUser ? 'You' : persona?.name || 'Marcus'}
                    </p>
                    {/* Message bubble */}
                    <div className={`
                      px-4 py-2.5 rounded-2xl text-sm leading-relaxed
                      ${msg.isUser 
                        ? 'bg-blue-500 text-white rounded-br-sm' 
                        : 'bg-slate-700 text-slate-100 rounded-bl-sm'
                      }
                    `}>
                      {msg.text}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Footer tip */}
        <div className="px-5 py-3 border-t border-slate-700/50 bg-slate-800/30">
          <p className="text-xs text-slate-500 text-center">
            💡 बेहतर परिणाम के लिए हिंदी में बोलें
          </p>
        </div>
      </div>
    </div>
  );
}


export default VoiceChat;
