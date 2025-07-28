import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { useApi } from '../contexts/ApiContext';
import { useLanguage } from '../contexts/LanguageContext';

const WikiAnalysis: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { fetchData } = useApi();
  const { t } = useLanguage();

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
      setSuccess(result.message || t('wikiAnalysis.successMessage'));
    } catch (err) {
      setError(t('wikiAnalysis.errorMessage'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('wikiAnalysis.title')}
      </Typography>
      <Typography paragraph color="text.secondary">
        {t('wikiAnalysis.description')}
      </Typography>
      <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
        <TextField
          margin="normal"
          required
          fullWidth
          id="wiki-url"
          label={t('wikiAnalysis.urlLabel')}
          name="url"
          autoComplete="url"
          autoFocus
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
          placeholder={t('wikiAnalysis.urlPlaceholder')}
        />
        <Button
          type="submit"
          fullWidth
          variant="contained"
          sx={{ mt: 3, mb: 2 }}
          disabled={loading || !url}
        >
          {loading ? <CircularProgress size={24} /> : t('wikiAnalysis.startButton')}
        </Button>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
      </Box>
    </Paper>
  );
};

export default WikiAnalysis; 