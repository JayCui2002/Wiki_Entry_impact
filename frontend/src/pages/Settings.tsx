import React from 'react';
import { 
  Box, 
  Typography, 
  Card, 
  CardContent, 
  FormControlLabel, 
  Switch, 
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Select,
  MenuItem,
  FormControl
} from '@mui/material';
import { 
  Brightness6 as DarkModeIcon,
  Language as LanguageIcon,
  Notifications as NotificationIcon,
  Storage as StorageIcon 
} from '@mui/icons-material';
import { useTheme } from '../contexts/ThemeContext';
import { useLanguage, Language } from '../contexts/LanguageContext';

const Settings: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { language, setLanguage, t } = useLanguage();

  const handleLanguageChange = (event: any) => {
    setLanguage(event.target.value as Language);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 3, color: 'text.primary' }}>
        {t('settings.title')}
      </Typography>

      {/* 外观设置 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <DarkModeIcon sx={{ mr: 1 }} />
            {t('settings.appearance')}
          </Typography>
          
          <List>
            <ListItem>
              <ListItemText 
                primary={t('settings.darkMode')}
                secondary={t('settings.darkModeDesc')}
              />
              <ListItemSecondaryAction>
                <FormControlLabel
                  control={
                    <Switch
                      checked={isDarkMode}
                      onChange={toggleDarkMode}
                      color="primary"
                    />
                  }
                  label=""
                />
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* 语言设置 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <LanguageIcon sx={{ mr: 1 }} />
            {t('settings.language')}
          </Typography>
          
          <List>
            <ListItem>
              <ListItemText 
                primary={t('settings.interfaceLanguage')}
                secondary={
                  language === 'zh' 
                    ? t('settings.currentLanguage').replace('简体中文', t('language.chinese'))
                    : t('settings.currentLanguage').replace('English', t('language.english'))
                }
              />
              <ListItemSecondaryAction>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <Select
                    value={language}
                    onChange={handleLanguageChange}
                    displayEmpty
                  >
                    <MenuItem value="zh">{t('language.chinese')}</MenuItem>
                    <MenuItem value="en">{t('language.english')}</MenuItem>
                  </Select>
                </FormControl>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* 通知设置 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <NotificationIcon sx={{ mr: 1 }} />
            {t('settings.notifications')}
          </Typography>
          
          <List>
            <ListItem>
              <ListItemText 
                primary={t('settings.analysisNotification')}
                secondary={t('settings.analysisNotificationDesc')}
              />
              <ListItemSecondaryAction>
                <Switch defaultChecked color="primary" />
              </ListItemSecondaryAction>
            </ListItem>
            
            <Divider />
            
            <ListItem>
              <ListItemText 
                primary={t('settings.systemNotification')}
                secondary={t('settings.systemNotificationDesc')}
              />
              <ListItemSecondaryAction>
                <Switch defaultChecked color="primary" />
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* 数据设置 */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <StorageIcon sx={{ mr: 1 }} />
            {t('settings.data')}
          </Typography>
          
          <List>
            <ListItem>
              <ListItemText 
                primary={t('settings.cacheManagement')}
                secondary={t('settings.cacheManagementDesc')}
              />
              <ListItemSecondaryAction>
                <Typography variant="body2" color="text.secondary">
                  约 15.2 MB
                </Typography>
              </ListItemSecondaryAction>
            </ListItem>
            
            <Divider />
            
            <ListItem>
              <ListItemText 
                primary={t('settings.dataExport')}
                secondary={t('settings.dataExportDesc')}
              />
              <ListItemSecondaryAction>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer' }}>
                  {t('common.export')}
                </Typography>
              </ListItemSecondaryAction>
            </ListItem>
          </List>
        </CardContent>
      </Card>

      {/* 版本信息 */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {t('settings.version')}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {t('settings.copyright')}
        </Typography>
      </Box>
    </Box>
  );
};

export default Settings; 