# 🎨 Frontend Tool Calling - Quick Start Guide

## What You're Building

A chat interface that shows **which tools the AI is using** and **what data it fetched**.

### Before
```
User: What's the wheat price in Delhi?
AI: The wheat price in Delhi is ₹2,150/quintal
```

### After  ✨
```
User: What's the wheat price in Delhi?

AI: The wheat price in Delhi is ₹2,150/quintal

🔧 1 Tool Used ▼
  ✓ get_market_prices
    Input: wheat, Delhi
    Result: ₹2,150/quintal (from data.gov.in API)
```

## 3 Steps to Implement

### Step 1: Copy the Component
```bash
# Copy React example to your project
cp examples/ChatIntegration.tsx src/components/ChatInterface.tsx
cp examples/ChatInterface.css src/components/ChatInterface.css
```

### Step 2: Update API Endpoint
In `ChatIntegration.tsx`, change:
```jsx
// Change this to your backend URL
const response = await fetch('/api/chat', {
  // ... rest of config
});
```

### Step 3: Use in Your App
```jsx
import ChatInterface from './components/ChatInterface';

export default function App() {
  return <ChatInterface />;
}
```

**That's it!** The tool tracking is automatic.

## API Response You'll Get

```json
{
  "response": "The wheat price in Delhi is ₹2,150/quintal",
  "timestamp": "2026-02-14T10:30:00",
  "tool_calls": [
    {
      "name": "get_market_prices",
      "description": "Gets real-time crop prices",
      "input": "wheat, Delhi",
      "output": "₹2,150/quintal (updated today)",
      "status": "success"
    }
  ]
}
```

## Component Features Out of the Box

✅ **Responsive Design**
- Desktop: 70% width chat bubbles
- Tablet: 85% width  
- Mobile: Full width

✅ **Tool Display**
- Collapsible by default (compact view)
- Shows tool name, input, output
- Color-coded status (green/red/blue)
- Copy-to-clipboard buttons

✅ **Loading States**
- Typing indicator animation
- Disabled buttons while waiting
- Visual feedback

✅ **Accessibility**
- Semantic HTML
- Keyboard navigation
- Color + icon indicators (not just color)
- ARIA labels ready

✅ **Animations**
- Smooth message entrance
- Tool section expansion
- Loading spinner

## Customization Examples

### Change Colors
```css
/* In ChatInterface.css */
.chat-interface {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Change send button color */
.send-button {
  background: #4CAF50;  /* ← Change this */
}

/* Change header color */
.chat-header {
  border-bottom: 3px solid #4CAF50;  /* ← Change this */
}
```

### Change Tool Display Format
```jsx
// In ChatIntegration.tsx - modify ToolCallDetail component
const formatToolName = (name: string) => {
  // Current: get_market_prices → Get Market Prices
  // Add emojis or icons here
  const icons: Record<string, string> = {
    'get_market_prices': '📊',
    'get_weather_forecast': '🌤️',
    'get_soil_and_irrigation_advice': '🌱'
  };
  return `${icons[name] || '🔧'} ${formatted_name}`;
};
```

### Add Dark Mode
```css
@media (prefers-color-scheme: dark) {
  .chat-interface {
    background: #1a1a1a;
  }
  .message {
    background: #2a2a2a;
    color: #eee;
  }
  /* ... etc */
}
```

### Customize Tool Icons
```jsx
// Replace in ToolCallDetail component
const getToolIcon = (status: string) => {
  return {
    'success': '✅',
    'error': '❌',
    'pending': '⏳'
  }[status];
};

// Then use it:
<span className="tool-icon">{getToolIcon(tool.status)}</span>
```

## Integration Checklist

- [ ] Copy `examples/ChatIntegration.tsx` to your project
- [ ] Copy `examples/ChatInterface.css` to your project
- [ ] Update API endpoint URL
- [ ] Install dependencies (if needed): `npm install react`
- [ ] Test with real backend
- [ ] Customize colors/styling for your brand
- [ ] Add dark mode support (optional)
- [ ] Test on mobile devices
- [ ] Test in different languages

## Testing

### Without Real Backend
```jsx
// Mock the API response in your test
const mockResponse = {
  response: "The weather is sunny",
  timestamp: new Date().toISOString(),
  tool_calls: [
    {
      name: "get_weather_forecast",
      description: "Gets weather data",
      input: "Delhi, today",
      output: "Sunny, 28°C",
      status: "success"
    }
  ]
};

// Then test the component with this data
```

### With Real Backend
```bash
# Start your backend
python start.py

# In browser:
# http://localhost:3000  (if frontend is on 3000)
# Type: "What is the weather?"
# See tools expand automatically
```

## Troubleshooting

### Tool calls not showing?
1. Check browser DevTools → Network → see API response
2. Verify `tool_calls` array is in response
3. Make sure `/api/chat` endpoint is responding correctly

### Styling looks broken?
1. Make sure `ChatInterface.css` is imported
2. Check for CSS conflicts with other frameworks
3. Clear browser cache (Ctrl+Shift+Delete)

### Component won't load?
1. Verify React is installed: `npm ls react`
2. Check TypeScript errors: `npx tsc --noEmit`
3. Ensure file paths are correct

## Advanced: Streaming Responses

For real-time tool visualization:

```jsx
// In sendMessage function
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: text, stream: true }),
  headers: { 'Content-Type': 'application/json' }
});

// Handle Server-Sent Events
const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');
  
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const event = JSON.parse(line.slice(6));
      
      if (event.type === 'tool_start') {
        // Show tool is being called
        console.log(`Calling ${event.tool_name}...`);
      } else if (event.type === 'tool_end') {
        // Show tool result
        console.log(`Got result: ${event.output}`);
      }
    }
  }
}
```

## File Structure

```
your-project/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx       (← Copy from examples/)
│   │   └── ChatInterface.css       (← Copy from examples/)
│   └── App.tsx
└── package.json
```

## Browser Support

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Component is lightweight (~50KB)
- Animations use GPU (smooth)
- No external UI libraries needed
- Message virtualization for 1000+ messages (optional enhancement)

## Next Steps

1. **Implement basic version** (Steps 1-3 above)
2. **Test with real data** (use actual Groq API key)
3. **Customize styling** (brand colors, fonts)
4. **Add features** (export chat, dark mode, etc.)
5. **Deploy** (Vercel, Netlify, etc.)

## Support Files

- 📄 **FRONTEND_GUIDE.md** - Complete code examples (React + Vue)
- 📄 **IMPLEMENTATION_SUMMARY.md** - Technical details
- 📁 **examples/** - Full working components

## Questions?

Check the examples folder for:
- Complete React component with all features
- Full CSS styling with responsive breakpoints
- Integration examples
- Dark mode support (customizable)

Good luck with your frontend! 🚀
