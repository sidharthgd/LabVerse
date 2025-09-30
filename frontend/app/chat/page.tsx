'use client'

import { useState } from 'react'
import ChatBox from '@/components/ChatBox'

export default function ChatPage() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">
            AI Data Assistant
          </h1>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <ChatBox 
              messages={messages}
              onSendMessage={(message) => {
                setMessages(prev => [...prev, {role: 'user', content: message}])
                // TODO: Send to backend API
              }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
