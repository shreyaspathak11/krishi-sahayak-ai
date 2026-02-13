// ChatIntegration.tsx - Complete React Example with Tool Display

import React, { useState, useCallback } from 'react';
import './ChatInterface.css';

interface ToolCall {
  name: string;
  description: string;
  input: string | object;
  output: string;
  status: 'success' | 'error' | 'pending';
}

interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
  toolCalls?: ToolCall[];
}

interface ChatResponse {
  response: string;
  timestamp: string;
  session_id?: string;
  tool_calls?: ToolCall[];
  thinking_process?: string;
  sources?: string[];
}

export const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateSessionId());
  const [language, setLanguage] = useState('en');

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return;

    // Add user message immediately
    const userMessageId = `user-${Date.now()}`;
    const userMessage: ChatMessage = {
      id: userMessageId,
      text,
      isUser: true,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: sessionId,
          language,
          chat_history: messages
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Add assistant message with tools
      const assistantMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        text: data.response,
        isUser: false,
        timestamp: data.timestamp,
        toolCalls: data.tool_calls
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: `error-${Date.now()}`,
        text: 'Failed to get response. Please try again.',
        isUser: false,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [messages, sessionId, language]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="chat-interface">
      <header className="chat-header">
        <h1>🌾 Krishi Sahayak</h1>
        <select 
          value={language} 
          onChange={(e) => setLanguage(e.target.value)}
          className="language-select"
        >
          <option value="en">English</option>
          <option value="hi">हिंदी</option>
          <option value="pa">ਪੰਜਾਬੀ</option>
          <option value="mr">मराठी</option>
          <option value="te">తెలుగు</option>
        </select>
      </header>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to Krishi Sahayak</h2>
            <p>Ask me about:</p>
            <ul>
              <li>🌤️ Weather forecasts</li>
              <li>📊 Crop market prices</li>
              <li>🌱 Soil and irrigation advice</li>
              <li>📰 Agricultural news</li>
              <li>🌾 Crop-specific guidance</li>
            </ul>
          </div>
        )}

        {messages.map((message) => (
          <div 
            key={message.id} 
            className={`message ${message.isUser ? 'user' : 'assistant'}`}
          >
            <div className="message-header">
              <span className="avatar">
                {message.isUser ? '👨‍🌾' : '🤖'}
              </span>
              <span className="time">
                {new Date(message.timestamp).toLocaleTimeString()}
              </span>
            </div>

            <div className="message-content">
              {message.text}
            </div>

            {/* Tool Calls Display */}
            {message.toolCalls && message.toolCalls.length > 0 && !message.isUser && (
              <ToolCallsDisplay toolCalls={message.toolCalls} />
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message assistant loading">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about weather, prices, crops..."
          disabled={isLoading}
          className="message-input"
          autoFocus
        />
        <button 
          type="submit" 
          disabled={isLoading || !input.trim()}
          className="send-button"
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};

// Tool Calls Component
const ToolCallsDisplay: React.FC<{ toolCalls: ToolCall[] }> = ({ toolCalls }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="tool-calls-container">
      <button 
        className="tool-toggle"
        onClick={() => setExpanded(!expanded)}
      >
        <span>🔧 {toolCalls.length} Tool{toolCalls.length > 1 ? 's' : ''} Used</span>
        <span className={`arrow ${expanded ? 'open' : ''}`}>▼</span>
      </button>

      {expanded && (
        <div className="tool-details">
          {toolCalls.map((tool, idx) => (
            <ToolCallDetail key={idx} tool={tool} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
};

// Individual Tool Call Component
const ToolCallDetail: React.FC<{ tool: ToolCall; index: number }> = ({ tool, index }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatToolName = (name: string) => {
    return name
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .trim()
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatInput = (input: any) => {
    return typeof input === 'string' ? input : JSON.stringify(input, null, 2);
  };

  return (
    <div className={`tool-call tool-${tool.status}`}>
      <div className="tool-header">
        <span className="tool-number">{index + 1}</span>
        <span className="tool-icon">
          {tool.status === 'success' ? '✓' : tool.status === 'error' ? '✗' : '⏳'}
        </span>
        <span className="tool-name">{formatToolName(tool.name)}</span>
        <span className={`tool-status ${tool.status}`}>
          {tool.status.toUpperCase()}
        </span>
      </div>

      <div className="tool-body">
        {tool.description && (
          <div className="tool-description">
            <small>{tool.description}</small>
          </div>
        )}

        <div className="tool-section">
          <label>Input:</label>
          <div className="tool-value-wrapper">
            <code>{formatInput(tool.input)}</code>
            <button
              className="copy-btn"
              onClick={() => copyToClipboard(formatInput(tool.input))}
              title="Copy to clipboard"
            >
              {copied ? '✓' : '📋'}
            </button>
          </div>
        </div>

        <div className="tool-section">
          <label>Output:</label>
          <div className="tool-value-wrapper">
            <code>{tool.output}</code>
            <button
              className="copy-btn"
              onClick={() => copyToClipboard(tool.output)}
              title="Copy to clipboard"
            >
              {copied ? '✓' : '📋'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper function
function generateSessionId(): string {
  return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

export default ChatInterface;
