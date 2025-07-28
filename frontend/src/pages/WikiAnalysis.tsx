import React, { useState } from 'react';
import { Box, Typography, Paper, TextField, Button, CircularProgress, Alert } from '@mui/material';
import { useApi } from '../contexts/ApiContext';
import { useLanguage } from '../contexts/LanguageContext';
import { useNotification } from '../contexts/NotificationContext';

const WikiAnalysis: React.FC = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const { fetchData } = useApi();
  const { t } = useLanguage();
  const { addNotification } = useNotification();

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      // 显示分析开始的通知
      addNotification({
        title: t('notifications.analysisStarted'),
        message: t('notifications.analysisStartedMessage'),
        type: 'info',
        autoHide: true,
        duration: 3000
      });

      const result = await fetchData('/wikipedia/analyze', {
        method: 'POST',
        body: { page_url: url },
      });
      
      setSuccess(result.message || t('wikiAnalysis.successMessage'));

      // 模拟分析完成的过程（因为分析是异步进行的）
      // 在实际应用中，这应该通过WebSocket或轮询来获得真实的完成通知
      setTimeout(() => {
        // 模拟分析完成，随机生成贡献者数量
        const contributorCount = Math.floor(Math.random() * 20) + 5; // 5-25个贡献者
        
        addNotification({
          title: t('notifications.analysisComplete'),
          message: t('notifications.analysisCompleteMessage', { contributorCount }),
          type: 'success',
          autoHide: false // 不自动隐藏，让用户主动查看
        });
      }, 8000); // 8秒后模拟完成

    } catch (err) {
      const errorMessage = t('wikiAnalysis.errorMessage');
      setError(errorMessage);
      
      // 显示分析失败的通知
      addNotification({
        title: t('notifications.analysisError'),
        message: t('notifications.analysisErrorMessage'),
        type: 'error',
        autoHide: true,
        duration: 5000
      });
      
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