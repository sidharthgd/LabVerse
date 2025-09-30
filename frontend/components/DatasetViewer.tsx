'use client'

interface File {
  id: string
  name: string
  type: string
  size: number
  modified: string
}

interface DatasetViewerProps {
  file: File | null
}

export default function DatasetViewer({ file }: DatasetViewerProps) {
  if (!file) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>Select a file to view its schema and preview</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="font-semibold text-lg">{file.name}</h3>
        <p className="text-sm text-gray-500">{file.type} • {file.size} bytes</p>
      </div>
      
      <div>
        <h4 className="font-medium mb-2">Schema</h4>
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-sm text-gray-600">
            Schema information will be displayed here
          </p>
        </div>
      </div>
      
      <div>
        <h4 className="font-medium mb-2">Preview</h4>
        <div className="bg-gray-50 p-3 rounded">
          <p className="text-sm text-gray-600">
            Data preview will be displayed here
          </p>
        </div>
      </div>
    </div>
  )
}
