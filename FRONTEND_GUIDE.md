# Frontend Guide: Elegant Tool Calling Display

## Updated API Response Format

The backend now returns tool information alongside the response:

```json
{
  "response": "The weather in Delhi tomorrow will be partly cloudy with temperatures between 22-28°C. There's a 20% chance of light rain.",
  "timestamp": "2026-02-14T10:30:00",
  "session_id": "sess_123",
  "tool_calls": [
    {
      "name": "get_weather_forecast",
      "description": "Gets weather forecast for a location",
      "input": "Delhi, tomorrow",
      "output": "Temperature: 22-28°C, Conditions: Partly cloudy, Precipitation: 20%",
      "status": "success"
    }
  ]
}
```

## Frontend Components for Elegant Display

### 1. **React Component Example**

```jsx
import React, { useState } from 'react';
import './ChatMessage.css';

export function ChatMessage({ message, isUser, toolCalls, timestamp }) {
  const [expandedTools, setExpandedTools] = useState(false);

  if (isUser) {
    return (
      <div className="message user-message">
        <div className="message-content">{message}</div>
        <span className="message-time">{formatTime(timestamp)}</span>
      </div>
    );
  }

  return (
    <div className="message assistant-message">
      {/* Main Response */}
      <div className="message-content">
        <div className="response-text">{message}</div>
      </div>

      {/* Tool Calls Info */}
      {toolCalls && toolCalls.length > 0 && (
        <div className="tool-calls-container">
          <button 
            className="tool-toggle"
            onClick={() => setExpandedTools(!expandedTools)}
          >
            🔧 {toolCalls.length} Tool{toolCalls.length > 1 ? 's' : ''} Used
            <span className={`arrow ${expandedTools ? 'expanded' : ''}`}>▼</span>
          </button>

          {expandedTools && (
            <div className="tool-calls-details">
              {toolCalls.map((tool, idx) => (
                <div key={idx} className={`tool-call ${tool.status}`}>
                  {/* Tool Header */}
                  <div className="tool-header">
                    <span className={`status-icon ${tool.status}`}>
                      {tool.status === 'success' ? '✓' : '⚠️'}
                    </span>
                    <span className="tool-name">{tool.name}</span>
                    <span className="tool-status">{tool.status}</span>
                  </div>

                  {/* Tool Details */}
                  <div className="tool-body">
                    <div className="tool-section">
                      <label>Input:</label>
                      <div className="tool-value">{tool.input}</div>
                    </div>
                    <div className="tool-section">
                      <label>Result:</label>
                      <div className="tool-value">{tool.output}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <span className="message-time">{formatTime(timestamp)}</span>
    </div>
  );
}

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}
```

### 2. **Accompanying CSS**

```css
/* ChatMessage.css */

.message {
  margin: 16px 0;
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 70%;
  word-wrap: break-word;
  animation: slideIn 0.3s ease-out;
}

.user-message {
  align-self: flex-end;
  background: #4CAF50;
  color: white;
  margin-left: auto;
  margin-right: 0;
}

.assistant-message {
  align-self: flex-start;
  background: #f5f5f5;
  color: #333;
  margin-right: auto;
  margin-left: 0;
}

.message-content {
  margin-bottom: 8px;
  line-height: 1.5;
}

.response-text {
  font-size: 15px;
  font-weight: 500;
}

.message-time {
  display: block;
  font-size: 12px;
  opacity: 0.6;
  margin-top: 4px;
}

/* Tool Calls Styling */
.tool-calls-container {
  margin-top: 12px;
  border-top: 1px solid #ddd;
  padding-top: 8px;
}

.tool-toggle {
  background: none;
  border: 1px solid #ddd;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  width: 100%;
  justify-content: space-between;
}

.tool-toggle:hover {
  background: #f0f0f0;
  border-color: #999;
}

.arrow {
  transition: transform 0.2s ease;
  display: inline-block;
}

.arrow.expanded {
  transform: rotate(180deg);
}

.tool-calls-details {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tool-call {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 10px;
  font-size: 13px;
}

.tool-call.success {
  border-left: 3px solid #4CAF50;
}

.tool-call.error {
  border-left: 3px solid #f44336;
  background: #ffebee;
}

.tool-call.pending {
  border-left: 3px solid #2196F3;
  background: #e3f2fd;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
}

.status-icon {
  font-size: 16px;
}

.tool-name {
  color: #1976D2;
  font-family: monospace;
  flex: 1;
}

.tool-status {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 3px;
  text-transform: uppercase;
  font-weight: 500;
}

.tool-call.success .tool-status {
  background: #c8e6c9;
  color: #2e7d32;
}

.tool-call.error .tool-status {
  background: #ffcdd2;
  color: #c62828;
}

.tool-body {
  margin-top: 8px;
}

.tool-section {
  margin-bottom: 8px;
  padding: 6px;
  background: #fafafa;
  border-radius: 4px;
}

.tool-section label {
  display: block;
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
  font-size: 12px;
  text-transform: uppercase;
}

.tool-value {
  padding: 6px;
  background: white;
  border-left: 2px solid #ddd;
  border-radius: 2px;
  font-family: monospace;
  font-size: 12px;
  color: #333;
  word-break: break-word;
  max-height: 150px;
  overflow-y: auto;
}

/* Animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .message {
    max-width: 85%;
  }
}
```

### 3. **Vue.js Component Example**

```vue
<template>
  <div class="chat-message" :class="{ 'user-msg': isUser, 'assistant-msg': !isUser }">
    <!-- User Message -->
    <div v-if="isUser" class="message-content">
      {{ message }}
    </div>

    <!-- Assistant Message -->
    <div v-else>
      <div class="message-content response-text">
        {{ message }}
      </div>

      <!-- Tool Calls Accordion -->
      <div v-if="toolCalls?.length" class="tool-calls-section">
        <button 
          class="tool-toggle"
          @click="expanded = !expanded"
          :aria-expanded="expanded"
        >
          <span>🔧 {{ toolCalls.length }} Tool{{ toolCalls.length > 1 ? 's' : '' }} Used</span>
          <span class="arrow" :class="{ open: expanded }">▼</span>
        </button>

        <Transition name="expand">
          <div v-show="expanded" class="tool-details">
            <div 
              v-for="(tool, idx) in toolCalls" 
              :key="idx"
              class="tool-item"
              :class="`status-${tool.status}`"
            >
              <div class="tool-header">
                <span class="icon">{{ tool.status === 'success' ? '✓' : '⚠️' }}</span>
                <span class="name">{{ formatToolName(tool.name) }}</span>
                <span class="badge">{{ tool.status }}</span>
              </div>

              <div class="tool-content">
                <div class="detail-row">
                  <label>Input:</label>
                  <code>{{ tool.input }}</code>
                </div>
                <div class="detail-row">
                  <label>Result:</label>
                  <code>{{ tool.output }}</code>
                </div>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <div class="message-time">{{ formatTime(timestamp) }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  message: String,
  isUser: Boolean,
  toolCalls: Array,
  timestamp: String
});

const expanded = ref(false);

function formatTime(isoString) {
  return new Date(isoString).toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
}

function formatToolName(name) {
  return name
    .replace(/_/g, ' ')
    .replace(/\b\w/g, l => l.toUpperCase());
}
</script>

<style scoped>
/* Scoped styles - similar to CSS example above */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
```

## Usage in Chat Component

```jsx
export function ChatWindow() {
  const [messages, setMessages] = useState([]);

  const handleSendMessage = async (userMessage) => {
    // Add user message
    setMessages(prev => [...prev, {
      text: userMessage,
      isUser: true,
      timestamp: new Date().toISOString()
    }]);

    // Call API
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        language: 'en'
      })
    });

    const data = await response.json();

    // Add assistant message with tool calls
    setMessages(prev => [...prev, {
      text: data.response,
      isUser: false,
      toolCalls: data.tool_calls,
      timestamp: data.timestamp
    }]);
  };

  return (
    <div className="chat-window">
      {messages.map((msg, idx) => (
        <ChatMessage 
          key={idx}
          message={msg.text}
          isUser={msg.isUser}
          toolCalls={msg.toolCalls}
          timestamp={msg.timestamp}
        />
      ))}
    </div>
  );
}
```

## Best Practices for Elegant Display

1. **Progressive Disclosure**: Tools info is hidden by default (collapsible)
2. **Visual Hierarchy**: 
   - Main response prominent
   - Tool info secondary
   - Status indicators clear (✓ for success, ⚠️ for errors)

3. **Color Coding**:
   - Green for successful tool calls
   - Red for errors
   - Blue for pending operations

4. **Responsive Design**: 
   - Works on mobile
   - Truncates long outputs
   - Scrollable for overflow

5. **User Transparency**:
   - Shows exactly what data was fetched
   - Builds trust through visibility
   - Helps debug issues

6. **Loading States**:
   - Smooth animations
   - Clear feedback during processing
   - Streaming responses (optional)

## Advanced: Streaming with Tool Events

For real-time visualization, modify the streaming endpoint:

```jsx
async function streamChatWithTools(message, onChunk, onToolCall) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, stream: true })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'tool_start') {
            onToolCall({ ...data, status: 'pending' });
          } else if (data.type === 'tool_end') {
            onToolCall({ ...data, status: 'success' });
          } else if (data.type === 'text') {
            onChunk(data.content);
          }
        } catch (e) {
          console.error('Failed to parse event:', e);
        }
      }
    }
  }
}
```

This creates a smooth, real-time experience where users see tools being called as they happen!
