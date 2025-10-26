import * as React from "react"
import { useDropzone, type Accept } from "react-dropzone"
import { Upload, X, FileText, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "./button"
import { Progress } from "./progress"

export interface UploadedFile {
  file: File
  id: string
  progress?: number
  status?: "pending" | "uploading" | "success" | "error"
  error?: string
}

interface FileDropzoneProps {
  onFilesChange: (files: UploadedFile[]) => void
  files: UploadedFile[]
  maxFiles?: number
  maxSize?: number // in MB
  accept?: Accept
  disabled?: boolean
  className?: string
}

export function FileDropzone({
  onFilesChange,
  files,
  maxFiles = 10,
  maxSize = 25,
  accept = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
      ".docx",
    ],
  },
  disabled = false,
  className,
}: FileDropzoneProps) {
  const maxSizeBytes = maxSize * 1024 * 1024

  const onDrop = React.useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      // Handle rejected files
      if (rejectedFiles.length > 0) {
        const rejectedWithErrors = rejectedFiles.map((rejected) => {
          const errors = rejected.errors.map((e: any) => {
            if (e.code === "file-too-large") {
              return `Each file must be ≤ ${maxSize} MB.`
            }
            if (e.code === "file-invalid-type") {
              return "Only PDF or DOCX are supported."
            }
            return e.message
          })
          return {
            file: rejected.file,
            id: `${rejected.file.name}-${Date.now()}`,
            status: "error" as const,
            error: errors[0],
          }
        })
        onFilesChange([...files, ...rejectedWithErrors])
        return
      }

      // Check max files limit
      if (files.length + acceptedFiles.length > maxFiles) {
        return
      }

      const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
        file,
        id: `${file.name}-${Date.now()}`,
        status: "pending" as const,
        progress: 0,
      }))

      onFilesChange([...files, ...newFiles])
    },
    [files, maxFiles, maxSize, onFilesChange]
  )

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept,
    maxSize: maxSizeBytes,
    maxFiles: maxFiles - files.length,
    disabled: disabled || files.length >= maxFiles,
    noClick: true,
    noKeyboard: false,
  })

  const removeFile = (id: string) => {
    onFilesChange(files.filter((f) => f.id !== id))
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B"
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
    return (bytes / (1024 * 1024)).toFixed(1) + " MB"
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer",
          isDragActive && "border-primary bg-primary/5",
          !isDragActive && "border-muted-foreground/25 hover:border-muted-foreground/50",
          (disabled || files.length >= maxFiles) &&
            "opacity-50 cursor-not-allowed pointer-events-none"
        )}
        aria-describedby="dropzone-description"
      >
        <input {...getInputProps()} />
        <Upload
          className="mx-auto h-12 w-12 text-muted-foreground"
          aria-hidden="true"
        />
        <div className="mt-4">
          <Button
            type="button"
            variant="outline"
            onClick={open}
            disabled={disabled || files.length >= maxFiles}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault()
                open()
              }
            }}
          >
            Select files
          </Button>
          <p className="mt-2 text-sm text-muted-foreground">
            or drag and drop
          </p>
        </div>
        <p
          id="dropzone-description"
          className="mt-2 text-xs text-muted-foreground"
        >
          PDF or DOCX up to {maxSize} MB each (max {maxFiles} files)
        </p>
      </div>

      {files.length > 0 && (
        <div className="space-y-2" role="list" aria-label="Uploaded files">
          {files.map((uploadedFile) => (
            <div
              key={uploadedFile.id}
              className="flex items-start gap-3 rounded-lg border p-3"
              role="listitem"
            >
              <FileText
                className="h-5 w-5 shrink-0 text-muted-foreground"
                aria-hidden="true"
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="truncate text-sm font-medium">
                    {uploadedFile.file.name}
                  </p>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6 shrink-0"
                    onClick={() => removeFile(uploadedFile.id)}
                    aria-label={`Remove ${uploadedFile.file.name}`}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatFileSize(uploadedFile.file.size)}
                </p>
                {uploadedFile.status === "uploading" && (
                  <div className="mt-2 space-y-1">
                    <Progress
                      value={uploadedFile.progress || 0}
                      className="h-1"
                    />
                    <p className="text-xs text-muted-foreground">
                      {uploadedFile.progress || 0}%
                    </p>
                  </div>
                )}
                {uploadedFile.status === "error" && uploadedFile.error && (
                  <p className="mt-1 text-xs text-destructive" role="alert">
                    {uploadedFile.error}
                  </p>
                )}
                {uploadedFile.status === "success" && (
                  <p className="mt-1 text-xs text-green-600">Uploaded</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

