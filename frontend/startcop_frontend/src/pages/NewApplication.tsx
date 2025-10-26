import * as React from "react"
import { useNavigate } from "react-router-dom"
import { Play, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { FileDropzone, type UploadedFile } from "@/components/ui/file-dropzone"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import { motion } from "framer-motion"


export default function NewApplication() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [files, setFiles] = React.useState<UploadedFile[]>([])
  const [isEvaluating, setIsEvaluating] = React.useState(false)
  const [evaluationProgress, setEvaluationProgress] = React.useState(0)

  // Simulate file upload progress
  React.useEffect(() => {
    const pendingFiles = files.filter((f) => f.status === "pending")
    if (pendingFiles.length === 0) return

    const uploadFile = async (file: UploadedFile) => {
      // Update status to uploading
      setFiles((prev) =>
        prev.map((f) =>
          f.id === file.id ? { ...f, status: "uploading", progress: 0 } : f
        )
      )

      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise((resolve) => setTimeout(resolve, 100))
        setFiles((prev) =>
          prev.map((f) => (f.id === file.id ? { ...f, progress: i } : f))
        )
      }

      // Mark as success
      setFiles((prev) =>
        prev.map((f) =>
          f.id === file.id ? { ...f, status: "success", progress: 100 } : f
        )
      )
    }

    pendingFiles.forEach(uploadFile)
  }, [files])

  const handleStartEvaluation = async () => {
    // Validate all requirements
    const validFiles = files.filter((f) => f.status === "success")
    if (validFiles.length === 0) {
      toast({
        title: "Files required",
        description: "Please upload at least one file to continue.",
        variant: "destructive",
      })
      return
    }

    // Start evaluation
    setIsEvaluating(true)
    setEvaluationProgress(0)

    // Simulate evaluation progress
    for (let i = 0; i <= 100; i += 5) {
      await new Promise((resolve) => setTimeout(resolve, 200))
      setEvaluationProgress(i)
    }

    // Show success message
    toast({
      title: "Evaluation complete",
      description: "Your compliance evaluation has been processed successfully.",
    })

    // Navigate to results (would be a real route in production)
    setTimeout(() => {
      setIsEvaluating(false)
      navigate("/reports/1")
    }, 1000)
  }


  const canProcess = () => {
    const validFiles = files.filter((f) => f.status === "success")
    return validFiles.length > 0
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Enhanced Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-accent-50 to-secondary-50">
        {/* Animated glass orbs with stronger gradients */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-gradient-to-r from-primary-500/30 to-accent-500/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-96 h-96 bg-gradient-to-r from-accent-500/30 to-primary-500/30 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-20 left-1/3 w-80 h-80 bg-gradient-to-r from-secondary-500/30 to-primary-500/30 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-40 right-1/3 w-64 h-64 bg-gradient-to-r from-primary-500/30 to-accent-500/30 rounded-full blur-3xl animate-pulse delay-3000"></div>
      </div>

      {/* Dotted Grid Background - Above gradient, below content */}
      <div className="absolute inset-0 opacity-30" style={{
        backgroundImage: `radial-gradient(circle, var(--color-primary-500) 1px, transparent 1px)`,
        backgroundSize: '40px 40px'
      }}></div>

      {/* Enhanced glass overlay */}
      <div className="absolute inset-0 bg-white/5 backdrop-blur-sm"></div>
      
      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-6 py-12">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-3xl font-bold text-foreground">New Analysis</h1>
            <p className="text-muted-foreground">
              Upload your documents for compliance analysis
            </p>
          </div>


          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mt-12"
          >
            <Card>
              <CardHeader>
                <CardTitle>Upload Documents</CardTitle>
                <CardDescription>
                  Drop files here or click to upload. We support PDF, DOCX, and other document formats.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FileDropzone
                  files={files}
                  onFilesChange={setFiles}
                  maxFiles={10}
                  maxSize={25}
                />
              </CardContent>
            </Card>
          </motion.div>



          {/* Process Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="flex justify-center"
          >
            <Button
              onClick={handleStartEvaluation}
              disabled={!canProcess()}
              size="lg"
              className="flex items-center px-8 py-6 text-lg"
            >
              <Play className="h-5 w-5 mr-2" />
              Process Documents
            </Button>
          </motion.div>
        </div>
      </main>

      {/* Evaluation Progress Modal */}
      <Dialog open={isEvaluating} onOpenChange={() => {}}>
        <DialogContent className="sm:max-w-md" hideCloseButton>
          <DialogHeader>
            <DialogTitle>Processing Documents</DialogTitle>
            <DialogDescription>
              Please wait while we analyze your documents against the selected frameworks.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Analysis Progress</span>
                <span className="font-medium text-foreground">{evaluationProgress}%</span>
              </div>
              <Progress value={evaluationProgress} className="h-2" />
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="h-2 w-2 bg-success rounded-full" />
                <span className="text-sm text-muted-foreground">Uploading documents</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`h-2 w-2 rounded-full ${evaluationProgress > 25 ? 'bg-success' : 'bg-muted'}`} />
                <span className="text-sm text-muted-foreground">Parsing content</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`h-2 w-2 rounded-full ${evaluationProgress > 50 ? 'bg-success' : 'bg-muted'}`} />
                <span className="text-sm text-muted-foreground">Analyzing compliance</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className={`h-2 w-2 rounded-full ${evaluationProgress > 75 ? 'bg-success' : 'bg-muted'}`} />
                <span className="text-sm text-muted-foreground">Generating report</span>
              </div>
            </div>
            
            <div className="flex items-center justify-center py-4">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

