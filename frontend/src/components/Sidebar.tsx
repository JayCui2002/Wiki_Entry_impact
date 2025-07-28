import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Drawer, List, ListItem, ListItemButton, ListItemText, Toolbar, Divider } from '@mui/material';
import { useLanguage } from '../contexts/LanguageContext';

const drawerWidth = 240;

const Sidebar: React.FC = () => {
  const { t } = useLanguage();
  
  const navItems = [
    { text: t('nav.dashboard'), path: '/' },
    { text: t('nav.wikiAnalysis'), path: '/wiki-analysis' },
    { text: t('nav.analysisHistory'), path: '/analysis-history' },
  ];

  const secondaryNavItems = [
    { text: t('nav.contributors'), path: '/contributors' },
    { text: t('nav.analytics'), path: '/analytics' },
    { text: t('nav.comparison'), path: '/comparison' },
    { text: t('nav.settings'), path: '/settings' },
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
      }}
    >
      <Toolbar />
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component={RouterLink} to={item.path}>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        {secondaryNavItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton component={RouterLink} to={item.path}>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
};

export default Sidebar; 