// src/components/ChatInterface.js

import React from 'react';
import './ChatInterface.css';

// --- Placeholder Components ---

const ChatInputBar = () => {
  return (
    <div className="chat-input-bar">
      <div className="input-field-placeholder">Type your query here...</div>
      <div className="button-placeholder">Upload Dataset</div>
      <div className="button-placeholder send-button">Send</div>
    </div>
  );
};

const ChatDisplayArea = () => {
  return (
    <div className="chat-display-area">
      {/* This SVG is a simple placeholder for the graph icon */}
      <svg width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
      <div className="chat-content-placeholder-bottom">
          <div className="line-short"></div>
          <div className="line-long"></div>
      </div>
    </div>
  );
};

const HistoryCard = ({ date, title, onClick, active }) => {
  return (
    <div
      onClick={onClick}
      className={`flex flex-col justify-between p-3 rounded-xl cursor-pointer transition-all duration-200 border 
        ${
          active
            ? "bg-gradient-to-r from-blue-600 to-blue-800 text-white border-transparent shadow-lg"
            : "bg-gray-800 hover:bg-gray-700 border-gray-700 text-gray-200"
        }`}
    >
      {/* Date */}
      <div className="text-xs text-gray-400 mb-1">{date}</div>

      {/* Chat title */}
      <div className="font-medium text-sm truncate">{title}</div>
    </div>
  );
};

const ChatHistorySidebar = () => {
  return (
    <aside className="chat-history-sidebar">
      <div className="sidebar-header">
        <h3>Chat History</h3>
        <div className="sidebar-toggle">»</div>
      </div>
      <div className="chat-history-list">
        <div className="history-item-placeholder"></div> 

      </div>
      <div className="new-chat-button-placeholder">+ New Chat</div>
    </aside>
  );
};


// --- Main Interface Template ---

const ChatInterface = () => {
  return (
    <div className="chat-interface-container">
      <main className="main-content">
        <ChatInputBar />
        <ChatDisplayArea />
      </main> 
    </div>
  );
};

export default ChatInterface;
