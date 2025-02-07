import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import checkmarkImg from '../assets/checkmark.png';
import paperclipImg from '../assets/paperclip.png';

const InputView: React.FC = () => {
    const [query, setQuery] = useState<string>('');
    const [file, setFile] = useState<File | null>(null);
    const [responseData, setResponseData] = useState(null);
    const navigate = useNavigate();


    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (query === '') return; // Prevent submitting if no query is entered

        const formData = new FormData();
        formData.append('query', query);
        if (file) formData.append('file', file);
        console.log("Form data being sent:", formData);

        try {
            const response = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();
            setResponseData(data);

            // Redirect to chatbot view
            navigate('/chat', { state: { responseData: data } });
            console.log(responseData);

        } catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files && event.target.files[0]) {
            setFile(event.target.files[0]);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSubmit(e as any);
        }
    };


    return (
        <div className="container">
            <h1>LabVerse</h1>
            <form className="input-wrapper" onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Type your query here..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleKeyDown(e)}
                />
                <button className="send-button" type="submit">
                    <img src={checkmarkImg} alt="Send" />
                </button>
            </form>

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
