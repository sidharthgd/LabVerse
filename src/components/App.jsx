// src/components/App.jsx
import React, { useState } from 'react';
import InputView from './InputView';
import ChatbotView from './ChatbotView';
import '../styles/styles.css';

const App = () => {
    const [showChat, setShowChat] = useState(false);

    return (
        <div>
            {showChat ? <ChatbotView /> : <InputView />}
        </div>
    );
};

export default App;