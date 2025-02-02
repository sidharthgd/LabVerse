// src/components/InputView.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';


const InputView = () => {
    const [query, setQuery] = useState('');
    let navigate = useNavigate();


    const handleSubmit = () => {
        if (query) {
            navigate('/chat');
        }
    };

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            alert(`Selected file: ${file.name}`);
        }
    };

    return (
        <div className="container">
            <h1>LabVerse</h1>
            <div className="input-wrapper">
                <input
                    type="text"
                    placeholder="Type your query here..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
                />
                <button className="send-button" onClick={handleSubmit}>
                    <img src={require('../assets/checkmark.png')} alt="Send" />
                </button>
            </div>
            <label className="paperclip-box" htmlFor="file-upload">
                <img src={require('../assets/paperclip.png')} alt="Paperclip" />
            </label>
            <input
                id="file-upload"
                type="file"
                accept=".csv, .xlsx"
                onChange={handleFileChange}
            />
        </div>
    );
};

export default InputView;