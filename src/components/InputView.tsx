import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import checkmarkImg from '../assets/checkmark.png';
import paperclipImg from '../assets/paperclip.png';

const InputView: React.FC = () => {
    const [query, setQuery] = useState<string>('');
    const navigate = useNavigate();

    const handleSubmit = () => {
        if (query) {
            navigate('/chat');
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
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
                    <img src={checkmarkImg} alt="Send" />
                </button>
            </div>
            <label className="paperclip-box" htmlFor="file-upload">
                <img src={paperclipImg} alt="Paperclip" />
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
