import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import '../styles/ChatbotView.css';

const ChatbotView: React.FC = () => {

    type Message = {
        text: string;
        sender: "User" | "AI";
    };

    const location = useLocation();
    const responseData = location.state?.responseData || null;
    const query = location.state?.query || "";

    // initialize messages with the query and API response
    const initialMessages: Message[] = [];

    if (query) {
        initialMessages.push({ text: query, sender: "User" });
    }

    if (responseData?.message) {
        initialMessages.push({ text: responseData.message, sender: "AI" });
    }

    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [userQuery, setUserQuery] = useState(""); // this is for new input in the chat

    const handleSend = async () => {
        if (userQuery.trim()) {
            // add the user's message immediately
            const newMessages: Message[] = [...messages, { text: userQuery, sender: "User" }];
            setMessages(newMessages);
            setUserQuery(""); // clear input field

            try {
                const response = await fetch("http://127.0.0.1:8000/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ query: userQuery }),
                });

                if (!response.ok) {
                    throw new Error("Failed to fetch AI response");
                }

                const data = await response.json();

                // update messages with AI response
                setMessages([...newMessages, { text: data.message, sender: "AI" }]);
            } catch (error) {
                console.error("Error sending message:", error);
                setMessages([...newMessages, { text: "Error fetching AI response.", sender: "AI" }]);
            }
        }
    };


    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    };

    return (
        <div className="chat-container">
            <div className="prevChat-container">
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
                        value={userQuery}
                        onChange={(e) => setUserQuery(e.target.value)}
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
