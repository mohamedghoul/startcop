import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Download, AlertTriangle, Trophy, FileText, Shield, AlertCircle, CheckCircle, Flag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';

function ReportPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  // Mock data for the report page
  const reportData = {
    id: id || '1',
    score: 85,
    totalScore: 100,
    frameworks: ['QFCRA', 'ISO 27001', 'GDPR'],
    date: '2024-10-20',
    status: 'completed',
    name: 'Q4 2024 Compliance Review',
  };

  // Mock gaps data
  const gaps = [
    {
      id: '1',
      title: 'Data Encryption at Rest',
      description: 'Personal data is not encrypted when stored in databases',
      risk: 'high' as const,
      framework: 'GDPR',
      impact: 'Potential data breach exposure',
    },
    {
      id: '2',
      title: 'Access Control Logging',
      description: 'Insufficient logging of user access to sensitive systems',
      risk: 'high' as const,
      framework: 'ISO 27001',
      impact: 'Unable to track unauthorized access attempts',
    },
    {
      id: '3',
      title: 'Data Retention Policy',
      description: 'Missing clear data retention and deletion procedures',
      risk: 'medium' as const,
      framework: 'QFCRA',
      impact: 'Non-compliance with data minimization principles',
    },
    {
      id: '4',
      title: 'Incident Response Plan',
      description: 'Security incident response procedures need updating',
      risk: 'medium' as const,
      framework: 'ISO 27001',
      impact: 'Delayed response to security incidents',
    },
    {
      id: '5',
      title: 'Privacy Impact Assessment',
      description: 'PIA documentation is incomplete for new data processing activities',
      risk: 'low' as const,
      framework: 'GDPR',
      impact: 'Insufficient privacy risk documentation',
    },
  ];

  const downloads = [
    {
      name: 'Full Compliance Report',
      description: 'Complete analysis with all findings and recommendations',
      type: 'PDF',
      size: '2.4 MB',
    },
    {
      name: 'Policy Document',
      description: 'Annotated policy document with compliance notes',
      type: 'PDF',
      size: '1.2 MB',
    },
    {
      name: 'Risk Assessment',
      description: 'Detailed risk assessment with recommendations',
      type: 'DOCX',
      size: '0.8 MB',
    },
  ];

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
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center space-x-4 mb-8"
          >
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigate('/')}
              className="glass-card border-white/20 hover:border-white/30"
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-foreground">Compliance Report</h1>
              <p className="text-muted-foreground">
                Analysis results and recommendations for {reportData.name}
              </p>
            </div>
          </motion.div>

          {/* Enhanced Score Summary Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="glass-card p-8 rounded-3xl border-2 border-primary-200/50 shadow-2xl">
              <div className="flex items-center space-x-8">
                {/* Left Side - Percentage (1/3) */}
                <div className="w-1/3 flex flex-col items-center">
                  <div className="relative mb-6">
                    {/* Animated Circle Progress */}
                    <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 120 120">
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        stroke="rgba(255, 255, 255, 0.2)"
                        strokeWidth="8"
                        fill="none"
                      />
                      <motion.circle
                        cx="60"
                        cy="60"
                        r="50"
                        stroke="url(#gradient)"
                        strokeWidth="8"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={`${2 * Math.PI * 50}`}
                        initial={{ strokeDashoffset: 2 * Math.PI * 50 }}
                        animate={{ strokeDashoffset: 2 * Math.PI * 50 * (1 - reportData.score / 100) }}
                        transition={{ duration: 2, ease: "easeInOut" }}
                      />
                      <defs>
                        <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="var(--color-primary-500)" />
                          <stop offset="100%" stopColor="var(--color-accent-500)" />
                        </linearGradient>
                      </defs>
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Trophy className="h-16 w-16 text-primary" />
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-5xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent mb-2">
                      {reportData.score}%
                    </div>
                    <p className="text-lg text-muted-foreground font-medium">
                      Overall Score
                    </p>
                  </div>
                </div>

                {/* Right Side - Statement and Gaps (2/3) */}
                <div className="w-2/3">
                  <div className="space-y-6">
                    {/* Score Statement */}
                    <div>
                      <h3 className="text-2xl font-bold text-foreground mb-3">
                        {reportData.score >= 80 
                          ? "Your application is comprehensive" 
                          : reportData.score >= 60 
                          ? "Your application is partially complete" 
                          : "Your application contains major risks"
                        }
                      </h3>
                      <p className="text-lg text-muted-foreground leading-relaxed">
                        {reportData.score >= 80 
                          ? "Your compliance posture is strong with only minor areas for improvement. Continue monitoring and maintaining your current standards."
                          : reportData.score >= 60 
                          ? "Your application shows good compliance foundations but requires attention to several key areas to reach full compliance."
                          : "Your application has significant compliance gaps that require immediate attention to avoid regulatory risks and potential penalties."
                        }
                      </p>
                    </div>

                    {/* Top 3 Most Important Gaps */}
                    <div>
                      <h4 className="text-lg font-semibold text-foreground mb-4 flex items-center">
                        <AlertTriangle className="h-5 w-5 text-warning mr-2" />
                        Key Areas Requiring Attention
                      </h4>
                      <ul className="space-y-3">
                        {gaps
                          .filter(gap => gap.risk === 'high')
                          .slice(0, 3)
                          .map((gap, index) => (
                            <li key={gap.id} className="flex items-start space-x-3">
                              <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full flex items-center justify-center mt-0.5">
                                <span className="text-xs font-bold text-white">{index + 1}</span>
                              </div>
                              <div className="flex-1">
                                <span className="font-medium text-foreground">{gap.title}</span>
                                <span className="text-muted-foreground ml-2">({gap.framework})</span>
                              </div>
                            </li>
                          ))}
                        {gaps.filter(gap => gap.risk === 'high').length < 3 && 
                          gaps
                            .filter(gap => gap.risk === 'medium')
                            .slice(0, 3 - gaps.filter(gap => gap.risk === 'high').length)
                            .map((gap, index) => (
                              <li key={gap.id} className="flex items-start space-x-3">
                                <div className="flex-shrink-0 w-6 h-6 bg-gradient-to-r from-warning-500 to-warning-600 rounded-full flex items-center justify-center mt-0.5">
                                  <span className="text-xs font-bold text-white">
                                    {gaps.filter(gap => gap.risk === 'high').length + index + 1}
                                  </span>
                                </div>
                                <div className="flex-1">
                                  <span className="font-medium text-foreground">{gap.title}</span>
                                  <span className="text-muted-foreground ml-2">({gap.framework})</span>
                                </div>
                              </li>
                            ))
                        }
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Manual Review Flag - Only show for low scores */}
              {reportData.score < 90 && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 }}
                  className="mt-6 p-4 bg-gradient-to-r from-error-50/80 to-warning-50/80 border border-error-200/50 rounded-2xl"
                >
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <Flag className="h-6 w-6 text-error" />
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-error-800 mb-1">
                        Manual Review Required
                      </h4>
                      <p className="text-sm text-error-700 leading-relaxed">
                        This score is under manual review due to significant compliance gaps. 
                        Please exercise caution and consult with compliance experts before making any decisions.
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <Badge className="bg-error-100 text-error-800 border-error-200 px-3 py-1 hover:bg-error-100">
                        CAUTION
                      </Badge>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Gaps Discovered Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="glass-card p-8 rounded-3xl border-white/20">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-foreground mb-2 flex items-center">
                  <AlertCircle className="h-8 w-8 text-warning mr-3" />
                  Compliance Gaps Discovered
                </h2>
                <p className="text-lg text-muted-foreground">
                  Critical areas requiring immediate attention
                </p>
              </div>
              
              <div className="space-y-6">
                {gaps.map((gap, index) => (
                  <motion.div
                    key={gap.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: 0.3 + index * 0.1 }}
                    className={`p-6 rounded-2xl border transition-all duration-300 hover:scale-[1.02] ${
                      gap.risk === 'high' 
                        ? 'bg-gradient-to-r from-error-50/50 to-error-100/30 border-error-200/50 hover:border-error-300/70' 
                        : gap.risk === 'medium'
                        ? 'bg-gradient-to-r from-warning-50/50 to-warning-100/30 border-warning-200/50 hover:border-warning-300/70'
                        : 'bg-gradient-to-r from-success-50/50 to-success-100/30 border-success-200/50 hover:border-success-300/70'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        {gap.risk === 'high' ? (
                          <AlertTriangle className="h-6 w-6 text-error" />
                        ) : gap.risk === 'medium' ? (
                          <AlertCircle className="h-6 w-6 text-warning" />
                        ) : (
                          <CheckCircle className="h-6 w-6 text-success" />
                        )}
                        <h3 className="text-xl font-semibold text-foreground">{gap.title}</h3>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge 
                          variant="outline" 
                          className={`px-3 py-1 text-sm font-medium ${
                            gap.risk === 'high' 
                              ? 'border-error-300 text-error-700 bg-error-50' 
                              : gap.risk === 'medium'
                              ? 'border-warning-300 text-warning-700 bg-warning-50'
                              : 'border-success-300 text-success-700 bg-success-50'
                          }`}
                        >
                          {gap.risk.toUpperCase()} RISK
                        </Badge>
                        <Badge variant="outline" className="px-3 py-1 text-sm font-medium">
                          {gap.framework}
                        </Badge>
                      </div>
                    </div>
                    
                    <p className="text-muted-foreground mb-4 text-lg leading-relaxed">
                      {gap.description}
                    </p>
                    
                    <div className="flex items-center space-x-2 text-sm">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground font-medium">Impact:</span>
                      <span className="text-foreground">{gap.impact}</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Downloads Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            <div className="glass-card p-8 rounded-3xl border-white/20">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-foreground mb-2 flex items-center">
                  <Download className="h-8 w-8 text-primary mr-3" />
                  Download Reports
                </h2>
                <p className="text-lg text-muted-foreground">
                  Access your detailed compliance reports and annotated documents
                </p>
              </div>
              
              <div className="space-y-4">
                {downloads.map((download, index) => (
                  <motion.div
                    key={download.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center justify-between p-6 rounded-2xl border border-white/20 hover:border-white/30 transition-all duration-300 hover:scale-[1.01]"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="h-12 w-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                        <FileText className="h-6 w-6 text-primary-foreground" />
                      </div>
                      <div>
                        <p className="font-semibold text-foreground text-lg">{download.name}</p>
                        <p className="text-muted-foreground">
                          {download.description} • {download.type} • {download.size}
                        </p>
                      </div>
                    </div>
                    <Button className="bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-primary-foreground px-6 py-2 rounded-xl">
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}

// Export the ReportPage component
export default ReportPage;
