import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { CssBaseline, Container, Box, Toolbar } from '@mui/material';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Contributors from './pages/Contributors';
import ContributorDetail from './pages/ContributorDetail';
import Analytics from './pages/Analytics';
import Comparison from './pages/Comparison';
import Settings from './pages/Settings';
import WikiAnalysis from './pages/WikiAnalysis';
import AnalysisHistory from './pages/AnalysisHistory';
import { ApiProvider } from './contexts/ApiContext';
import { CustomThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { NotificationProvider } from './contexts/NotificationContext';
import './App.css'; // 导入全局过渡样式

const App: React.FC = () => {
  return (
    <LanguageProvider>
      <CustomThemeProvider>
        <CssBaseline />
        <NotificationProvider>
          <ApiProvider>
            <Router>
              <Box sx={{ display: 'flex' }}>
                <Header />
                <Sidebar />
                <Box
                  component="main"
                  sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
                >
                  <Toolbar />
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/contributors" element={<Contributors />} />
                    <Route path="/contributors/:id" element={<ContributorDetail />} />
                    <Route path="/analytics" element={<Analytics />} />
                    <Route path="/comparison" element={<Comparison />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/wiki-analysis" element={<WikiAnalysis />} />
                    <Route path="/analysis-history" element={<AnalysisHistory />} />
                  </Routes>
                </Box>
              </Box>
            </Router>
          </ApiProvider>
        </NotificationProvider>
      </CustomThemeProvider>
    </LanguageProvider>
  );
};

export default App; 