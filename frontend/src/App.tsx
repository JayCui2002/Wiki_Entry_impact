import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Container } from '@mui/material';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Contributors from './pages/Contributors';
import ContributorDetail from './pages/ContributorDetail';
import Analytics from './pages/Analytics';
import Comparison from './pages/Comparison';
import Settings from './pages/Settings';
import { ApiProvider } from './contexts/ApiContext';

// Create Material-UI theme with custom colors
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ApiProvider>
        <Router>
          <div style={{ display: 'flex', minHeight: '100vh' }}>
            <Sidebar />
            <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Header />
              <Container maxWidth="xl" sx={{ mt: 2, mb: 4, flexGrow: 1 }}>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/contributors" element={<Contributors />} />
                  <Route path="/contributors/:id" element={<ContributorDetail />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/comparison" element={<Comparison />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </Container>
            </div>
          </div>
        </Router>
      </ApiProvider>
    </ThemeProvider>
  );
};

export default App; 