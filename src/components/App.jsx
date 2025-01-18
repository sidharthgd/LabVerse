// App.js or index.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InputView from './InputView';
import ChatbotView from './ChatbotView';

const App = () => {
    // return (
    //     <Router>
    //         <Routes>
    //             <Route path="/" element={<InputView />} />
    //             <Route path="/chat" element={<ChatbotView />} />
    //         </Routes>
    //     </Router>
    // );
    return (
        <div>
            <InputView />
        </div>
    );
};

export default App;
