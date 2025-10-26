import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import ReportPage from './pages/ReportPage.tsx'
import NewApplication from './pages/NewApplication'
import { Toaster } from './components/ui/toaster'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/reports/:id" element={<ReportPage />} />
        <Route path="/new" element={<NewApplication />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  )
} 

export default App
