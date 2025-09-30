'use client'

interface File {
  id: string
  name: string
  type: string
  size: number
  modified: string
}

interface FileExplorerProps {
  files: File[]
  onFileSelect: (file: File | null) => void
}

export default function FileExplorer({ files, onFileSelect }: FileExplorerProps) {
  return (
    <div className="space-y-2">
      {files.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No files found. Connect your data sources to get started.</p>
        </div>
      ) : (
        files.map((file) => (
          <div
            key={file.id}
            onClick={() => onFileSelect(file)}
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center">
                📄
              </div>
              <div>
                <p className="font-medium">{file.name}</p>
                <p className="text-sm text-gray-500">{file.type}</p>
              </div>
            </div>
            <div className="text-sm text-gray-500">
              {file.size} bytes
            </div>
          </div>
        ))
      )}
    </div>
  )
}
