/**
 * Contributor Impact Dashboard Component
 * 贡献者影响分析仪表板组件
 * 
 * This component provides a comprehensive dashboard for analyzing 
 * Wikipedia contributor impact metrics, including additive vs 
 * maintenance contributions, discussion impact, and GDPR compliance.
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  IconButton,
  Tooltip,
  Alert,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  TrendingUp,
  Edit,
  Forum,
  Star,
  Visibility,
  VisibilityOff,
  Refresh,
  Download,
  Delete,
  Security,
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from 'recharts';

// Type definitions for component props and data
interface ContributorMetrics {
  contributorId: number;
  username: string;
  displayName: string;
  overallImpactScore: number;
  additiveScore: number;
  maintenanceScore: number;
  discussionScore: number;
  qualityScore: number;
  collaborationScore: number;
  totalEdits: number;
  pagesCreated: number;
  revertRate: number;
  isActive: boolean;
  contributionType: string;
  lastDataUpdate: string;
}

interface ImpactTrend {
  date: string;
  additiveContributions: number;
  maintenanceContributions: number;
  discussionParticipation: number;
}

interface ContributorDashboardProps {
  contributorId?: number;
}

const ContributorDashboard: React.FC<ContributorDashboardProps> = ({
  contributorId,
}) => {
  // State management for component data
  const [contributor, setContributor] = useState<ContributorMetrics | null>(null);
  const [impactTrends, setImpactTrends] = useState<ImpactTrend[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showPersonalData, setShowPersonalData] = useState<boolean>(false);
  const [refreshing, setRefreshing] = useState<boolean>(false);

  // Chart color scheme
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Mock data for demonstration (in real app, fetch from API)
  const mockContributor: ContributorMetrics = {
    contributorId: 1,
    username: 'WikiExpert2023',
    displayName: 'Dr. Sarah Johnson',
    overallImpactScore: 78.5,
    additiveScore: 82.3,
    maintenanceScore: 74.1,
    discussionScore: 68.9,
    qualityScore: 91.2,
    collaborationScore: 76.5,
    totalEdits: 1247,
    pagesCreated: 23,
    revertRate: 0.034,
    isActive: true,
    contributionType: 'Content Creator',
    lastDataUpdate: '2023-12-08T10:30:00Z',
  };

  const mockTrends: ImpactTrend[] = [
    { date: '2023-01', additiveContributions: 45, maintenanceContributions: 32, discussionParticipation: 12 },
    { date: '2023-02', additiveContributions: 52, maintenanceContributions: 38, discussionParticipation: 15 },
    { date: '2023-03', additiveContributions: 48, maintenanceContributions: 42, discussionParticipation: 18 },
    { date: '2023-04', additiveContributions: 61, maintenanceContributions: 45, discussionParticipation: 22 },
    { date: '2023-05', additiveContributions: 55, maintenanceContributions: 48, discussionParticipation: 19 },
    { date: '2023-06', additiveContributions: 68, maintenanceContributions: 52, discussionParticipation: 25 },
  ];

  // Load component data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // In real implementation, fetch data from API
        setContributor(mockContributor);
        setImpactTrends(mockTrends);
        setError(null);
      } catch (err) {
        setError('Failed to load contributor data');
        console.error('Error loading data:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [contributorId]);

  // Handle data refresh
  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      // Simulate API refresh
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update last data update timestamp
      if (contributor) {
        setContributor({
          ...contributor,
          lastDataUpdate: new Date().toISOString(),
        });
      }
    } catch (err) {
      setError('Failed to refresh data');
    } finally {
      setRefreshing(false);
    }
  };

  // Prepare chart data
  const contributionTypeData = contributor ? [
    { name: 'Additive', value: contributor.additiveScore, color: COLORS[0] },
    { name: 'Maintenance', value: contributor.maintenanceScore, color: COLORS[1] },
    { name: 'Discussion', value: contributor.discussionScore, color: COLORS[2] },
  ] : [];

  const scoreProgressData = contributor ? [
    { label: 'Overall Impact', value: contributor.overallImpactScore },
    { label: 'Quality Score', value: contributor.qualityScore },
    { label: 'Collaboration', value: contributor.collaborationScore },
  ] : [];

  // Render loading state
  if (loading) {
    return (
      <Box sx={{ p: 4 }}>
        <Typography variant="h6" gutterBottom>Loading contributor data...</Typography>
        <LinearProgress />
      </Box>
    );
  }

  // Render error state
  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" action={
          <Button color="inherit" size="small" onClick={() => window.location.reload()}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      </Box>
    );
  }

  // Render main dashboard
  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Contributor Impact Analysis
          </Typography>
          <Typography variant="subtitle1" color="text.secondary">
            {contributor?.isActive ? 'Active Contributor' : 'Inactive Contributor'}
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} disabled={refreshing}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Key Metrics Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <TrendingUp color="primary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="primary">
                {contributor?.overallImpactScore.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Overall Impact Score
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Edit color="secondary" sx={{ fontSize: 40, mb: 1 }} />
              <Typography variant="h4" color="secondary">
                {contributor?.totalEdits.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Edits
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Star sx={{ color: '#ff9800', fontSize: 40, mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#ff9800' }}>
                {contributor?.pagesCreated}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pages Created
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Forum sx={{ color: '#4caf50', fontSize: 40, mb: 1 }} />
              <Typography variant="h4" sx={{ color: '#4caf50' }}>
                {((1 - (contributor?.revertRate || 0)) * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Quality Rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Contribution Type Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contribution Type Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={contributionTypeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {contributionTypeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Impact Trends Over Time */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Impact Trends Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={impactTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="additiveContributions" 
                    stroke={COLORS[0]} 
                    name="Additive"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="maintenanceContributions" 
                    stroke={COLORS[1]} 
                    name="Maintenance"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="discussionParticipation" 
                    stroke={COLORS[2]} 
                    name="Discussion"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Metrics */}
      <Grid container spacing={3}>
        {/* Score Progress Bars */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              {scoreProgressData.map((metric, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{metric.label}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {metric.value.toFixed(1)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={metric.value}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: 'rgba(0,0,0,0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 4,
                        backgroundColor: COLORS[index % COLORS.length],
                      },
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Contributor Classification */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Contributor Profile
              </Typography>
              
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Classification
                </Typography>
                <Chip
                  label={contributor?.contributionType}
                  color="primary"
                  sx={{ mt: 1 }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Status
                </Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    label={contributor?.isActive ? 'Active' : 'Inactive'}
                    color={contributor?.isActive ? 'success' : 'default'}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                </Box>
              </Box>

              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last Data Update
                </Typography>
                <Typography variant="body2">
                  {contributor ? new Date(contributor.lastDataUpdate).toLocaleString() : 'N/A'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ContributorDashboard; 