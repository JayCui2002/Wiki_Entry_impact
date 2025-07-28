import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  FormControlLabel,
  Divider,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { useTheme } from '../contexts/ThemeContext';
import { useLanguage, Language } from '../contexts/LanguageContext';

const Settings: React.FC = () => {
  const { isDarkMode, toggleDarkMode } = useTheme();
  const { language, setLanguage, t } = useLanguage();
  const [analysisNotifications, setAnalysisNotifications] = useState(true);
  const [systemNotifications, setSystemNotifications] = useState(true);

  const handleLanguageChange = (event: any) => {
    setLanguage(event.target.value as Language);
  };

  const handleClearCache = () => {
    // 清除缓存的逻辑
    localStorage.clear();
    window.location.reload();
  };

  const handleExportData = () => {
    // 导出数据的逻辑
    alert(t('settings.dataExportInProgress'));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        {t('settings.title')}
      </Typography>

      {/* 外观设置 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {t('settings.appearance')}
        </Typography>
        <FormControlLabel
          control={
            <Switch
              checked={isDarkMode}
              onChange={toggleDarkMode}
            />
          }
          label={
            <Box>
              <Typography variant="body1">{t('settings.darkMode')}</Typography>
              <Typography variant="body2" color="text.secondary">
                {t('settings.darkModeDesc')}
              </Typography>
            </Box>
          }
        />
      </Paper>

      {/* 语言设置 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {t('settings.language')}
        </Typography>
        <FormControl fullWidth sx={{ maxWidth: 300 }}>
          <InputLabel>{t('settings.interfaceLanguage')}</InputLabel>
          <Select
            value={language}
            label={t('settings.interfaceLanguage')}
            onChange={handleLanguageChange}
          >
            <MenuItem value="zh">{t('language.chinese')}</MenuItem>
            <MenuItem value="en">{t('language.english')}</MenuItem>
          </Select>
        </FormControl>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          {language === 'zh' ? t('settings.currentLanguage') : 'Current: English'}
        </Typography>
      </Paper>

      {/* 通知设置 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {t('settings.notifications')}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={analysisNotifications}
                onChange={(e) => setAnalysisNotifications(e.target.checked)}
              />
            }
            label={
              <Box>
                <Typography variant="body1">{t('settings.analysisNotification')}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('settings.analysisNotificationDesc')}
                </Typography>
              </Box>
            }
          />
          <FormControlLabel
            control={
              <Switch
                checked={systemNotifications}
                onChange={(e) => setSystemNotifications(e.target.checked)}
              />
            }
            label={
              <Box>
                <Typography variant="body1">{t('settings.systemNotification')}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('settings.systemNotificationDesc')}
                </Typography>
              </Box>
            }
          />
        </Box>
      </Paper>

      {/* 数据设置 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          {t('settings.data')}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Box>
            <Typography variant="body1" gutterBottom>
              {t('settings.cacheManagement')}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {t('settings.cacheManagementDesc')}
            </Typography>
            <Button variant="outlined" onClick={handleClearCache}>
              {t('common.clearCache')}
            </Button>
          </Box>
          <Divider />
          <Box>
            <Typography variant="body1" gutterBottom>
              {t('settings.dataExport')}
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              {t('settings.dataExportDesc')}
            </Typography>
            <Button variant="outlined" onClick={handleExportData}>
              {t('common.exportData')}
            </Button>
          </Box>
        </Box>
      </Paper>

      {/* 版本信息 */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          {t('settings.version')}
          <br />
          {t('settings.copyright')}
        </Typography>
      </Paper>
    </Box>
  );
};

export default Settings; 