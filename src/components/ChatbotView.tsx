import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import '../styles/ChatbotView.css';

const ChatbotView: React.FC = () => {

    type Message = {
        text: string;
        sender: "User" | "AI";
    };

    const location = useLocation();
    const initialMessages = location.state?.responseData?.messages || [];
    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [query, setQuery] = useState("");

    const handleSend = () => {
        if (query.trim()) {
            const newMessages: Message[] = [...messages, { text: query, sender: "User" }];
            setMessages(newMessages);
            setQuery(""); // Clear input

            // Simulating AI response (Replace with API call)
            setTimeout(() => {
                setMessages([...newMessages, { text: "AI Response to: " + query, sender: "AI" } as Message]);
            }, 1000);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="chat-container"> 
            <div className = "prevChat-container">
                <h3 style={{ color: 'white' }}> Previous chats will go here</h3>
                
            </div>
            <div className="messages-container">
                <div className="chat-box">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.sender}`}>
                            {msg.text}
                        </div>
                    ))}
                </div>
                <div className="chat-input">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleKeyDown(e)}
                        placeholder="Type your message..."
                    />
                    <button onClick={handleSend}></button>
                </div>
            </div>
        </div>
    );
};

export default ChatbotView;
