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

        if (query.trim() === '') return; // Prevent submitting if no query is entered

        try {
            let response: Response;
            if (!file) {
                console.log("submitting query to API without file")
                response = await fetch('http://127.0.0.1:8000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query: query }),
                });
            } else {
                const formData = new FormData();
                formData.append('query', query);
                formData.append('file', file);

                response = await fetch('http://127.0.0.1:8000/upload', {
                    method: 'POST',
                    body: formData,
                });
            }

            const contentType = response.headers.get("Content-Type");

            if (contentType && contentType.includes("text/csv")) {
                // If response is CSV, parse as text
                const csvText = await response.text();
                console.log("CSV Response:", csvText);

                // Do something with the CSV data (e.g., display or download)
            } 

            const data = await response.json();
            console.log("API Response:", data); // log the API response
            setResponseData(data);

            // Redirect to chatbot view
            navigate('/chat', { state: { query: query, responseData: data } });

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
