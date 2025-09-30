'use client'

import { useState, useEffect } from 'react'
import FileExplorer from '@/components/FileExplorer'
import DatasetViewer from '@/components/DatasetViewer'

export default function FilesPage() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [files, setFiles] = useState([])

  useEffect(() => {
    // TODO: Fetch files from backend API
    setFiles([])
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Data Explorer
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Files & Datasets</h2>
            <FileExplorer 
              files={files}
              onFileSelect={setSelectedFile}
            />
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Dataset Preview</h2>
            <DatasetViewer 
              file={selectedFile}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
