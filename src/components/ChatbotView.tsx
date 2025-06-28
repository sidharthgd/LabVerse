import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { FaFolder, FaFileAlt, FaFileCsv, FaFileExcel, FaFileCode, FaChevronDown, FaChevronRight, FaCopy, FaPlay } from 'react-icons/fa';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import '../styles/ChatbotView.css';

const ChatbotView: React.FC = () => {

    type Message = {
        text: string;
        sender: "User" | "AI";
        timestamp: Date;
        code?: string;
        execution_result?: string;
        code_type?: string;
        attachments?: Array<{
            type: 'plot' | 'data' | 'file';
            url?: string;
            content?: string;
            filename?: string;
        }>;
    };

    const location = useLocation();
    const responseData = location.state?.responseData || null;
    const query = location.state?.query || "";

    // initialize messages with the query and API response
    const initialMessages: Message[] = [];

    if (query) {
        initialMessages.push({ 
            text: query, 
            sender: "User", 
            timestamp: new Date() 
        });
    }

    if (responseData?.message) {
        initialMessages.push({ 
            text: responseData.message, 
            sender: "AI", 
            timestamp: new Date(),
            code: responseData.code,
            execution_result: responseData.execution_result,
            code_type: responseData.code_type
        });
    }

    const [messages, setMessages] = useState<Message[]>(initialMessages);
    const [userQuery, setUserQuery] = useState(""); // this is for new input in the chat
    const [isLoading, setIsLoading] = useState(false);
    const [availableFiles, setAvailableFiles] = useState<string[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // Load available files on component mount
    useEffect(() => {
        fetchAvailableFiles();
    }, []);

    const fetchAvailableFiles = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/files');
            if (response.ok) {
                const files = await response.json();
                setAvailableFiles(files.files || []);
            }
        } catch (error) {
            console.error('Error fetching files:', error);
        }
    };

    const handleSend = async () => {
        if (userQuery.trim() && !isLoading) {
            setIsLoading(true);
            
            // add the user's message immediately
            const newMessages: Message[] = [...messages, { 
                text: userQuery, 
                sender: "User", 
                timestamp: new Date() 
            }];
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

                // Process attachments if any
                const attachments: Message['attachments'] = [];
                if (data.plot_url) {
                    attachments.push({
                        type: 'plot' as const,
                        url: data.plot_url,
                        filename: data.plot_filename
                    });
                }
                if (data.data_export) {
                    attachments.push({
                        type: 'data' as const,
                        content: data.data_export,
                        filename: data.data_filename
                    });
                }

                // update messages with AI response including code and execution results
                setMessages([...newMessages, { 
                    text: data.message, 
                    sender: "AI", 
                    timestamp: new Date(),
                    code: data.code,
                    execution_result: data.execution_result,
                    code_type: data.code_type || 'python',
                    attachments
                }]);
            } catch (error) {
                console.error("Error sending message:", error);
                setMessages([...newMessages, { 
                    text: "Error fetching AI response.", 
                    sender: "AI", 
                    timestamp: new Date() 
                }]);
            } finally {
                setIsLoading(false);
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const formatMessage = (text: string) => {
        // Convert markdown-like formatting to HTML
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    };

    const downloadData = (content: string, filename: string) => {
        const blob = new Blob([content], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    };

    const getFileIcon = (filename: string) => {
        const extension = filename.split('.').pop()?.toLowerCase();
        switch (extension) {
            case 'csv':
                return <FaFileCsv style={{ color: '#4CAF50', marginRight: '8px' }} />;
            case 'xlsx':
            case 'xls':
                return <FaFileExcel style={{ color: '#1B7535', marginRight: '8px' }} />;
            case 'json':
                return <FaFileCode style={{ color: '#FF9800', marginRight: '8px' }} />;
            default:
                return <FaFileAlt style={{ color: '#2196F3', marginRight: '8px' }} />;
        }
    };

    const renderAttachments = (attachments: Message['attachments']) => {
        if (!attachments || attachments.length === 0) return null;

        return (
            <div className="message-attachments">
                {attachments.map((attachment, index) => (
                    <div key={index} className="attachment">
                        {attachment.type === 'plot' && attachment.url && (
                            <div className="plot-attachment">
                                <img src={attachment.url} alt="Data visualization" />
                                <button 
                                    onClick={() => window.open(attachment.url, '_blank')}
                                    className="download-btn"
                                >
                                    View Full Size
                                </button>
                            </div>
                        )}
                        {attachment.type === 'data' && attachment.content && (
                            <div className="data-attachment">
                                <div className="data-preview">
                                    <pre>{attachment.content.substring(0, 200)}...</pre>
                                </div>
                                <button 
                                    onClick={() => downloadData(attachment.content!, attachment.filename || 'data.csv')}
                                    className="download-btn"
                                >
                                    Download Data
                                </button>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        );
    };

    const CodeBlock: React.FC<{ 
        code: string; 
        language: string; 
        executionResult?: string; 
    }> = ({ code, language, executionResult }) => {
        const [isExpanded, setIsExpanded] = useState(false);
        const [copied, setCopied] = useState(false);

        const copyToClipboard = async () => {
            try {
                await navigator.clipboard.writeText(code);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
            }
        };

        return (
            <div className="code-block-container">
                <div className="code-block-header" onClick={() => setIsExpanded(!isExpanded)}>
                    <div className="code-block-title">
                        {isExpanded ? <FaChevronDown /> : <FaChevronRight />}
                        <FaFileCode style={{ marginLeft: '8px', marginRight: '8px' }} />
                        <span>Generated {language.toUpperCase()} Code</span>
                    </div>
                    <div className="code-block-actions">
                        <button 
                            className="code-action-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                copyToClipboard();
                            }}
                            title="Copy code"
                        >
                            <FaCopy />
                            {copied && <span className="copy-feedback">Copied!</span>}
                        </button>
                    </div>
                </div>
                
                {isExpanded && (
                    <div className="code-block-content">
                        <SyntaxHighlighter
                            language={language}
                            style={tomorrow}
                            showLineNumbers={true}
                            wrapLines={true}
                            customStyle={{
                                margin: 0,
                                borderRadius: '0 0 8px 8px',
                                fontSize: '14px'
                            }}
                        >
                            {code}
                        </SyntaxHighlighter>
                        
                        {executionResult && (
                            <div className="execution-result">
                                <div className="execution-result-header">
                                    <FaPlay style={{ marginRight: '8px' }} />
                                    <span>Execution Result</span>
                                </div>
                                <pre className="execution-result-content">
                                    {executionResult}
                                </pre>
                            </div>
                        )}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="chat-container">
            <div className="sidebar">
                <div className="sidebar-section">
                    <h3><FaFolder style={{ color: '#FFB74D', marginRight: '8px' }} />Available Files</h3>
                    <div className="file-list">
                        {availableFiles.map((file, index) => (
                            <div key={index} className="file-item">
                                {getFileIcon(file)}
                                {file}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <div className="messages-container">
                <div className="chat-header">
                    <h2>LabVerse</h2>
                    <p>Your intelligent laboratory data analysis companion</p>
                </div>
                
                <div className="chat-box">
                    {messages.map((msg, index) => (
                        <div key={index} className={`message ${msg.sender}`}>
                            <div className="message-content">
                                <div 
                                    className="message-text"
                                    dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }}
                                />
                                
                                {/* Render code block if present */}
                                {msg.code && (
                                    <CodeBlock 
                                        code={msg.code}
                                        language={msg.code_type || 'python'}
                                        executionResult={msg.execution_result}
                                    />
                                )}
                                
                                {/* Render existing attachments */}
                                {renderAttachments(msg.attachments)}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div className="message AI">
                            <div className="loading-indicator">
                                <div className="typing-dots">
                                    <span></span>
                                    <span></span>
                                    <span></span>
                                </div>
                                Analyzing your query...
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
                
                <div className="chat-input">
                    <input
                        type="text"
                        value={userQuery}
                        onChange={(e) => setUserQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask about your laboratory data..."
                        disabled={isLoading}
                    />
                    <button 
                        onClick={handleSend} 
                        disabled={isLoading || !userQuery.trim()}
                        className="send-button"
                    >
                        {isLoading ? '⏳' : '➤'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatbotView;
