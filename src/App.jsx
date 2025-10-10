// src/App.js

import React from 'react';
import ChatInterface from './components/ChatInterface';
import TargetCursor from "./components/TargetCursor"
import ClickSpark from "./components/ClickSpark"
function App() {
  return (
    
       <ClickSpark
  sparkColor='#fff'
  sparkSize={10}
  sparkRadius={25}
  sparkCount={12}
  duration={400}
>
    <div className="App">
   
      <ChatInterface />
    </div>
    </ClickSpark>
  );
}

export default App;