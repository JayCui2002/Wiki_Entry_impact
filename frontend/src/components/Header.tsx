import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  IconButton, 
  Box,
  Tooltip,
  Menu,
  MenuItem
} from '@mui/material';
import { 
  Brightness6 as DarkModeIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { useLanguage, Language } from '../contexts/LanguageContext';

const drawerWidth = 240;

const Header: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { language, setLanguage, t } = useLanguage();
  const navigate = useNavigate();
  
  const [languageAnchorEl, setLanguageAnchorEl] = React.useState<null | HTMLElement>(null);
  const [isThemeToggling, setIsThemeToggling] = React.useState(false);

  const handleLanguageMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setLanguageAnchorEl(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setLanguageAnchorEl(null);
  };

  const handleLanguageChange = (newLanguage: Language) => {
    setLanguage(newLanguage);
    handleLanguageMenuClose();
  };

  const handleThemeToggle = () => {
    setIsThemeToggling(true);
    toggleDarkMode();
    // 重置状态，与主题切换时间同步
    setTimeout(() => {
      setIsThemeToggling(false);
    }, 150);
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        width: `calc(100% - ${drawerWidth}px)`,
        ml: `${drawerWidth}px`,
        zIndex: (theme) => theme.zIndex.drawer + 1
      }}
    >
      <Toolbar>
        <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
          {t('header.title')}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {/* 通知按钮 */}
          <Tooltip title={t('header.notifications')}>
            <IconButton color="inherit" sx={{ mr: 1 }}>
              <NotificationsIcon />
            </IconButton>
          </Tooltip>
          
          {/* 语言切换按钮 */}
          <Tooltip title={t('settings.interfaceLanguage')}>
            <IconButton 
              color="inherit" 
              onClick={handleLanguageMenuOpen}
              sx={{ mr: 1 }}
            >
              <LanguageIcon />
            </IconButton>
          </Tooltip>
          
          {/* Dark Mode 切换按钮 */}
          <Tooltip title={isDarkMode ? t('header.toggleLightMode') : t('header.toggleDarkMode')}>
            <IconButton 
              color="inherit" 
              onClick={handleThemeToggle} 
              sx={{ 
                mr: 1,
                '& .MuiSvgIcon-root': {
                  transition: 'color 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                  opacity: isThemeToggling ? 0.7 : 1,
                }
              }}
            >
              <DarkModeIcon />
            </IconButton>
          </Tooltip>
          
          {/* 设置按钮 */}
          <Tooltip title={t('header.settings')}>
            <IconButton 
              color="inherit" 
              onClick={() => navigate('/settings')}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
        
        {/* 语言选择菜单 */}
        <Menu
          anchorEl={languageAnchorEl}
          open={Boolean(languageAnchorEl)}
          onClose={handleLanguageMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem 
            onClick={() => handleLanguageChange('zh')}
            selected={language === 'zh'}
          >
            {t('language.chinese')}
          </MenuItem>
          <MenuItem 
            onClick={() => handleLanguageChange('en')}
            selected={language === 'en'}
          >
            {t('language.english')}
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 