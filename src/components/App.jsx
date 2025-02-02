import React from 'react';
import { HashRouter as Router, Routes, Route } from 'react-router-dom';
import InputView from './InputView';
import ChatbotView from './ChatbotView';

const App = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<InputView />} />
                <Route path="/chat" element={<ChatbotView />} />
            </Routes>
        </Router>
    );
};

export default App;
