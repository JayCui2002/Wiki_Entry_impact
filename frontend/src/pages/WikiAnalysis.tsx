import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { useApi } from '../contexts/ApiContext';

const WikiAnalysis: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { fetchData } = useApi(); // We will use this later

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await fetchData('/wikipedia/analyze', {
        method: 'POST',
        body: { page_url: url },
      });
      setSuccess(result.message || 'Analysis has been successfully queued.');
    } catch (err) {
      setError('Failed to start analysis. Please check the URL and try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Analyze Wikipedia Page
      </Typography>
      <Typography paragraph color="text.secondary">
        Enter the full URL of a Wikipedia page to fetch its history, analyze its contributors, and calculate their impact scores.
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="wiki-url"
          label="Wikipedia Page URL"
          name="url"
          autoComplete="url"
          autoFocus
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading || !url}
        >
          {loading ? <CircularProgress size={24} /> : 'Start Analysis'}
        </Button>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
      </Box>
    </Paper>
  );
};

export default WikiAnalysis; 