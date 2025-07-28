import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar
} from '@mui/material';
import { 
  Timeline as TimelineIcon, 
  Group as GroupIcon, 
  Article as ArticleIcon,
  Visibility as ViewIcon,
  Delete as DeleteIcon 
} from '@mui/icons-material';
import { useApi } from '../contexts/ApiContext';
import { useLanguage } from '../contexts/LanguageContext';

interface AnalysisSession {
  id: number;
  page_title: string;
  page_url: string;
  analysis_status: string;
  total_contributors_found: number;
  total_revisions_analyzed: number;
  started_at: string;
  completed_at?: string;
  error_message?: string;
}

interface Contributor {
  id: number;
  wikipedia_username: string;
  display_name: string;
  overall_impact_score: number;
  total_edits: number;
  contributor_type: string;
}

const AnalysisHistory: React.FC = () => {
  const [sessions, setSessions] = useState<AnalysisSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<AnalysisSession | null>(null);
  const [contributors, setContributors] = useState<Contributor[]>([]);
  const [contributorsLoading, setContributorsLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { fetchData } = useApi();
  const { t } = useLanguage();

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await fetchData('/analysis-sessions/');
      setSessions(data);
    } catch (err) {
      setError(t('analysisHistory.loadError'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadContributors = async (sessionId: number) => {
    try {
      setContributorsLoading(true);
      const data = await fetchData(`/analysis-sessions/${sessionId}/contributors`);
      setContributors(data);
    } catch (err) {
      console.error('Failed to load contributors:', err);
      setContributors([]);
    } finally {
      setContributorsLoading(false);
    }
  };

  const handleViewSession = async (session: AnalysisSession) => {
    setSelectedSession(session);
    setDialogOpen(true);
    await loadContributors(session.id);
  };

  const handleDeleteSession = async (sessionId: number) => {
    if (window.confirm('Are you sure you want to delete this analysis session?')) {
      try {
        await fetchData(`/analysis-sessions/${sessionId}`, { method: 'DELETE' });
        await loadSessions(); // Reload the list
      } catch (err) {
        console.error('Failed to delete session:', err);
      }
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'processing': return 'warning';
      case 'failed': return 'error';
      default: return 'default';
    }
  };

  const getContributorTypeColor = (type: string) => {
    switch (type) {
      case 'Architect': return '#1976d2';
      case 'Gardener': return '#388e3c';
      case 'Artisan': return '#f57c00';
      case 'Newcomer': return '#757575';
      default: return '#757575';
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <>
      <Paper sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" mb={3}>
          <TimelineIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h4">{t('analysisHistory.title')}</Typography>
        </Box>
        
        <Typography paragraph color="text.secondary">
          {t('analysisHistory.description')}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {sessions.length === 0 ? (
          <Alert severity="info">
            {t('analysisHistory.noSessions')}
          </Alert>
        ) : (
          <Grid container spacing={3}>
            {sessions.map((session) => (
              <Grid item xs={12} md={6} lg={4} key={session.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <ArticleIcon sx={{ mr: 1 }} />
                      <Typography variant="h6" noWrap>
                        {session.page_title}
                      </Typography>
                    </Box>
                    
                    <Chip 
                      label={session.analysis_status} 
                      color={getStatusColor(session.analysis_status) as any}
                      size="small"
                      sx={{ mb: 2 }}
                    />
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {t('analysisHistory.contributors')}: {session.total_contributors_found}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {t('analysisHistory.revisions')}: {session.total_revisions_analyzed}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary">
                      {t('analysisHistory.started')}: {new Date(session.started_at).toLocaleDateString()}
                    </Typography>
                    
                    {session.error_message && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        {session.error_message}
                      </Alert>
                    )}
                  </CardContent>
                  
                  <CardActions>
                    <Button 
                      startIcon={<ViewIcon />}
                      onClick={() => handleViewSession(session)}
                      disabled={session.analysis_status !== 'completed'}
                    >
                      View
                    </Button>
                    <Button 
                      startIcon={<DeleteIcon />}
                      color="error"
                      onClick={() => handleDeleteSession(session.id)}
                    >
                      Delete
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Contributors Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedSession?.page_title} - Contributors
        </DialogTitle>
        
        <DialogContent>
          {contributorsLoading ? (
            <Box display="flex" justifyContent="center" p={3}>
              <CircularProgress />
            </Box>
          ) : contributors.length === 0 ? (
            <Alert severity="info">
              No contributors found in this analysis session.
            </Alert>
          ) : (
            <List>
              {contributors.map((contributor) => (
                <ListItem key={contributor.id}>
                  <ListItemAvatar>
                    <Avatar 
                      sx={{ 
                        bgcolor: getContributorTypeColor(contributor.contributor_type || 'Newcomer') 
                      }}
                    >
                      <GroupIcon />
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={contributor.wikipedia_username}
                    secondary={
                      <Box>
                        <Typography component="span" variant="body2">
                          Impact Score: {contributor.overall_impact_score?.toFixed(1) || 'N/A'}
                        </Typography>
                        <br />
                        <Typography component="span" variant="body2" color="text.secondary">
                          Total Edits: {contributor.total_edits || 0} • 
                          Type: {contributor.contributor_type || 'Newcomer'}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default AnalysisHistory; 