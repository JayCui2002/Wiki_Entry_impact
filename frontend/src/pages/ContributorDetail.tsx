import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, Paper, Alert, CircularProgress, Grid } from '@mui/material';
import { useApi } from '../contexts/ApiContext';

const ContributorDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [contributor, setContributor] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { fetchData } = useApi();

  useEffect(() => {
    if (!id) return;

    const getContributorDetail = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchData(`/contributors/${id}`, { include_detailed: true });
        setContributor(data);
      } catch (err) {
        setError('Failed to fetch contributor details.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    getContributorDetail();
  }, [id, fetchData]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!contributor) {
    return <Alert severity="info">No contributor data found.</Alert>;
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Contributor Detail: {contributor.display_name}
      </Typography>
      <Paper sx={{ p: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="h6">ID:</Typography>
            <Typography>{contributor.id}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="h6">Wikipedia Username:</Typography>
            <Typography>{contributor.wikipedia_username}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="h6">Impact Score:</Typography>
            <Typography>{contributor.overall_impact_score?.toFixed(2)}</Typography>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="h6">Primary Language:</Typography>
            <Typography>{contributor.primary_language}</Typography>
          </Grid>
           <Grid item xs={12}>
            <Typography variant="h6">Detailed Metrics:</Typography>
            <pre>{JSON.stringify(contributor.detailed_metrics, null, 2)}</pre>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ContributorDetail; 