import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import InputView from './components/InputView';
import ChatbotView from './components/ChatbotView';
import './styles/styles.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<InputView />} />
        <Route path="/chat" element={<ChatbotView />} />
      </Routes>
    </Router>
  );
}

export default App;
