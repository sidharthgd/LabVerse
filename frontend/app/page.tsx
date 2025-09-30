import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Welcome to LabVerse
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Connect your data sources and start analyzing with AI-powered insights
          </p>
          
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <Link 
              href="/chat" 
              className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
            >
              <h2 className="text-2xl font-semibold mb-4">Start Chatting</h2>
              <p className="text-gray-600">
                Ask questions about your data and get AI-powered insights
              </p>
            </Link>
            
            <Link 
              href="/files" 
              className="bg-white p-8 rounded-lg shadow-lg hover:shadow-xl transition-shadow"
            >
              <h2 className="text-2xl font-semibold mb-4">Explore Files</h2>
              <p className="text-gray-600">
                Browse your connected data sources and datasets
              </p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
