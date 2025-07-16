import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Drawer, List, ListItem, ListItemButton, ListItemText, Toolbar, Divider } from '@mui/material';

const drawerWidth = 240;

const Sidebar: React.FC = () => {
  const navItems = [
    { text: 'Dashboard', path: '/' },
    { text: 'Wiki Analysis', path: '/wiki-analysis' },
    { text: 'Analysis History', path: '/analysis-history' },
  ];

  const secondaryNavItems = [
    { text: 'Contributors', path: '/contributors' },
    { text: 'Analytics', path: '/analytics' },
    { text: 'Comparison', path: '/comparison' },
    { text: 'Settings', path: '/settings' },
  ]

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