import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { ArrowRight, Upload, FileText, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();

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
      
      {/* Centered Hero Section */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
            className="space-y-8"
          >
            {/* Main heading */}
            <div className="space-y-6">
              <h1 className="text-6xl md:text-8xl font-bold bg-gradient-to-r from-primary-600 via-primary-700 to-primary-800 bg-clip-text text-transparent leading-tight drop-shadow-lg">
                STARTCOP
              </h1>
              <p className="text-2xl md:text-3xl text-foreground font-medium leading-relaxed max-w-3xl mx-auto">
                Intelligent Compliance Analysis
              </p>
              <p className="text-lg md:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
                Upload your documents and get instant analysis against regulatory frameworks. 
                Save time, reduce errors, and ensure compliance with our AI-powered platform.
              </p>
            </div>

            {/* CTA Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="flex flex-col sm:flex-row gap-6 justify-center items-center"
            >
              <Button
                size="lg"
                onClick={() => navigate('/new')}
                className="text-xl px-12 py-6 bg-gradient-to-r from-primary-600 via-primary-700 to-primary-800 hover:from-primary-700 hover:via-primary-800 hover:to-primary-900 text-primary-foreground border-0 rounded-full shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105 ring-4 ring-primary-200/50 hover:ring-primary-300/70"
              >
                Get Started
                <ArrowRight className="ml-3 h-6 w-6" />
              </Button>
            </motion.div>

            {/* Feature highlights */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16"
            >
              <div className="glass-card p-8 rounded-2xl">
                <div className="h-16 w-16 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Upload className="h-8 w-8 text-primary-foreground" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Easy Upload</h3>
                <p className="text-muted-foreground">Drag and drop your documents for instant analysis</p>
              </div>

              <div className="glass-card p-8 rounded-2xl">
                <div className="h-16 w-16 bg-gradient-to-r from-accent-500 to-accent-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-8 w-8 text-accent-foreground" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Compliance Check</h3>
                <p className="text-muted-foreground">Analyze against multiple regulatory frameworks</p>
              </div>

              <div className="glass-card p-8 rounded-2xl">
                <div className="h-16 w-16 bg-gradient-to-r from-secondary-500 to-secondary-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FileText className="h-8 w-8 text-secondary-foreground" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-2">Detailed Reports</h3>
                <p className="text-muted-foreground">Get comprehensive reports with actionable insights</p>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
