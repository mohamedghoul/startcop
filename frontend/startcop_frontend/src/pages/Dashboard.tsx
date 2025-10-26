import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, FileText, CheckCircle, Clock, TrendingUp, BarChart3, Users, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import StatCard from '@/components/ui/stat-card';
import Navigation from '@/components/Navigation';
import { motion } from 'framer-motion';

export default function Dashboard() {
  const navigate = useNavigate();

  // Mock data for dashboard
  const stats = {
    totalApplications: 24,
    completedThisMonth: 8,
    averageScore: 87,
    frameworksSupported: 12,
  };

  const recentApplications = [
    {
      id: '1',
      name: 'Q4 2024 Compliance Review',
      frameworks: ['QFCRA', 'ISO 27001'],
      status: 'completed',
      date: '2024-10-20',
      score: 87,
    },
    {
      id: '2',
      name: 'AML/KYC Assessment',
      frameworks: ['AML/KYC'],
      status: 'in_progress',
      date: '2024-10-23',
      progress: 45,
    },
    {
      id: '3',
      name: 'GDPR Compliance Check',
      frameworks: ['GDPR', 'ISO 27001'],
      status: 'completed',
      date: '2024-10-18',
      score: 92,
    },
    {
      id: '4',
      name: 'PCI DSS Audit',
      frameworks: ['PCI DSS'],
      status: 'pending',
      date: '2024-10-25',
    },
  ];

  const quickActions = [
    {
      title: 'New Analysis',
      description: 'Start a new compliance analysis',
      icon: Plus,
      action: () => navigate('/dashboard/new'),
      variant: 'primary' as const,
    },
    {
      title: 'View Reports',
      description: 'Browse all completed reports',
      icon: FileText,
      action: () => navigate('/dashboard/reports'),
      variant: 'secondary' as const,
    },
    {
      title: 'Frameworks',
      description: 'Explore supported frameworks',
      icon: Shield,
      action: () => navigate('/frameworks'),
      variant: 'outline' as const,
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container section">
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
              <p className="text-muted-foreground">
                Overview of your compliance analyses and reports
              </p>
            </div>
            <Button
              onClick={() => navigate('/dashboard/new')}
              size="lg"
              className="w-full md:w-auto"
            >
              <Plus className="mr-2 h-5 w-5" />
              New Analysis
            </Button>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Applications"
              value={stats.totalApplications}
              description="All time"
              icon={FileText}
              trend={{
                value: 12,
                label: "vs last month",
                isPositive: true,
              }}
            />
            <StatCard
              title="Completed This Month"
              value={stats.completedThisMonth}
              description="October 2024"
              icon={CheckCircle}
              trend={{
                value: 25,
                label: "vs last month",
                isPositive: true,
              }}
            />
            <StatCard
              title="Average Score"
              value={`${stats.averageScore}%`}
              description="Across all reports"
              icon={TrendingUp}
              trend={{
                value: 5,
                label: "vs last month",
                isPositive: true,
              }}
            />
            <StatCard
              title="Frameworks Supported"
              value={stats.frameworksSupported}
              description="Available for analysis"
              icon={Shield}
            />
          </div>

          {/* Quick Actions */}
          <div className="grid gap-6 md:grid-cols-3">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <motion.div
                  key={action.title}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card 
                    variant="interactive" 
                    className="cursor-pointer"
                    onClick={action.action}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center space-x-4">
                        <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                          <Icon className="h-6 w-6 text-primary" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-semibold text-foreground">{action.title}</h3>
                          <p className="text-sm text-muted-foreground">{action.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>

          {/* Recent Applications */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="h-5 w-5 mr-2" />
                Recent Applications
              </CardTitle>
              <CardDescription>
                Your latest compliance evaluations and their status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentApplications.map((app, index) => (
                  <motion.div
                    key={app.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.4, delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="space-y-1">
                      <p className="font-medium text-foreground">{app.name}</p>
                      <div className="flex items-center gap-2">
                        {app.frameworks.map((fw) => (
                          <Badge key={fw} variant="outline" className="text-xs">
                            {fw}
                          </Badge>
                        ))}
                      </div>
                      <p className="text-sm text-muted-foreground">{app.date}</p>
                    </div>
                    <div className="text-right">
                      {app.status === 'completed' && (
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-5 w-5 text-success" />
                          <span className="font-semibold text-success">
                            {app.score}%
                          </span>
                        </div>
                      )}
                      {app.status === 'in_progress' && (
                        <div className="flex items-center gap-2">
                          <Clock className="h-5 w-5 text-warning" />
                          <span className="text-sm text-muted-foreground">
                            {app.progress}% complete
                          </span>
                        </div>
                      )}
                      {app.status === 'pending' && (
                        <Badge variant="status-pending">
                          Pending
                        </Badge>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}