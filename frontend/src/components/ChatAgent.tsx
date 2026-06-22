import React, { useState } from 'react';

interface Message {
    sender: 'user' | 'agent';
    text: string;
}

interface ChatAgentProps {
    messages: Message[];
    onSendMessage: (text: string) => void;
    loading: boolean;
}

const ChatAgent: React.FC<ChatAgentProps> = ({ messages, onSendMessage, loading }) => {
  const [input, setInput] = useState('');
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };
  return (
    <div className="chat-messages-container glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '20px' }}>
      <div className="chat-messages" style={{ flexGrow: 1, overflowY: 'auto' }}>
        {messages.map((msg, index) => (
          <div key={index} className={`chat-bubble ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {loading && (
          <div className="chat-bubble agent" style={{ opacity: 0.6 }}>
            Thinking...
          </div>
        )}
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          type="text"
          placeholder="Ask WeEat for recommendations..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="chat-input"
          disabled={loading}
        />
        <button type="submit" className="submit-btn" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatAgent;