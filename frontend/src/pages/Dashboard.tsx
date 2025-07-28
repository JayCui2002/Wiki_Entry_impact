import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, CircularProgress, Alert } from '@mui/material';
import PeopleIcon from '@mui/icons-material/People';
import StarIcon from '@mui/icons-material/Star';
import { useApi } from '../contexts/ApiContext';
import { useLanguage } from '../contexts/LanguageContext';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactElement;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon }) => (
  <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
    {icon}
    <Box sx={{ ml: 2 }}>
      <Typography color="text.secondary">{title}</Typography>
      <Typography variant="h5" component="p">
        {value}
      </Typography>
    </Box>
  </Paper>
);

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { fetchData } = useApi();
  const { t } = useLanguage();

  useEffect(() => {
    const getStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchData('/contributors/stats/overview');
        setStats(data);
      } catch (err) {
        setError(t('dashboard.fetchError') || 'Failed to fetch dashboard stats.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getStats();
  }, [fetchData, t]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>{t('common.loading')}</Typography>
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {t('dashboard.title')}
      </Typography>
      {stats && (
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title={t('dashboard.totalContributors')}
              value={stats.total_contributors || 0}
              icon={<PeopleIcon color="primary" sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title={t('dashboard.averageImpact')}
              value={stats.average_impact_score?.toFixed(2) || '0.00'}
              icon={<StarIcon color="secondary" sx={{ fontSize: 40 }} />}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <StatCard
              title={t('dashboard.activeContributors')}
              value={stats.active_contributors || 0}
              icon={<PeopleIcon color="success" sx={{ fontSize: 40 }} />}
            />
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default Dashboard; 