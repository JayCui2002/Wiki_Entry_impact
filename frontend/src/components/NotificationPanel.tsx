import React, { useState } from 'react';
import {
  Popover,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  IconButton,
  Box,
  Divider,
  Button,
  Chip,
  useTheme,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  MarkEmailRead as MarkReadIcon,
  DeleteSweep as ClearIcon,
} from '@mui/icons-material';
import { useNotification, Notification } from '../contexts/NotificationContext';
import { useLanguage } from '../contexts/LanguageContext';

interface NotificationPanelProps {
  anchorEl: HTMLElement | null;
  open: boolean;
  onClose: () => void;
}

const NotificationPanel: React.FC<NotificationPanelProps> = ({ anchorEl, open, onClose }) => {
  const { notifications, markAsRead, markAllAsRead, removeNotification, clearAll } = useNotification();
  const { t } = useLanguage();
  const theme = useTheme();

  // 获取通知图标
  const getNotificationIcon = (type: Notification['type']) => {
    const iconProps = { fontSize: 'small' as const };
    switch (type) {
      case 'success':
        return <SuccessIcon color="success" {...iconProps} />;
      case 'error':
        return <ErrorIcon color="error" {...iconProps} />;
      case 'warning':
        return <WarningIcon color="warning" {...iconProps} />;
      case 'info':
        return <InfoIcon color="info" {...iconProps} />;
      default:
        return <InfoIcon color="info" {...iconProps} />;
    }
  };

  // 格式化时间
  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    
    if (diff < 60000) { // 小于1分钟
      return t('notifications.justNow');
    } else if (diff < 3600000) { // 小于1小时
      const minutes = Math.floor(diff / 60000);
      return t('notifications.minutesAgo', { minutes });
    } else if (diff < 86400000) { // 小于1天
      const hours = Math.floor(diff / 3600000);
      return t('notifications.hoursAgo', { hours });
    } else {
      return timestamp.toLocaleDateString();
    }
  };

  // 处理通知点击
  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
  };

  return (
    <Popover
      open={open}
      anchorEl={anchorEl}
      onClose={onClose}
      anchorOrigin={{
        vertical: 'bottom',
        horizontal: 'right',
      }}
      transformOrigin={{
        vertical: 'top',
        horizontal: 'right',
      }}
      PaperProps={{
        sx: {
          width: 400,
          maxHeight: 500,
          overflow: 'hidden',
        },
      }}
    >
      <Paper>
        {/* 标题栏 */}
        <Box
          sx={{
            p: 2,
            borderBottom: `1px solid ${theme.palette.divider}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Typography variant="h6">
            {t('notifications.title')}
          </Typography>
          <Box>
            {notifications.length > 0 && (
              <>
                <IconButton
                  size="small"
                  onClick={markAllAsRead}
                  title={t('notifications.markAllRead')}
                  sx={{ mr: 1 }}
                >
                  <MarkReadIcon fontSize="small" />
                </IconButton>
                <IconButton
                  size="small"
                  onClick={clearAll}
                  title={t('notifications.clearAll')}
                >
                  <ClearIcon fontSize="small" />
                </IconButton>
              </>
            )}
          </Box>
        </Box>

        {/* 通知列表 */}
        <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
          {notifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="text.secondary">
                {t('notifications.empty')}
              </Typography>
            </Box>
          ) : (
            <List sx={{ p: 0 }}>
              {notifications.map((notification, index) => (
                <React.Fragment key={notification.id}>
                  <ListItem
                    sx={{
                      backgroundColor: notification.read ? 'transparent' : theme.palette.action.hover,
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: theme.palette.action.selected,
                      },
                    }}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <ListItemIcon sx={{ minWidth: 40 }}>
                      {getNotificationIcon(notification.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <Typography
                            variant="subtitle2"
                            sx={{ 
                              fontWeight: notification.read ? 'normal' : 'bold',
                              flexGrow: 1,
                              mr: 1
                            }}
                          >
                            {notification.title}
                          </Typography>
                          <IconButton
                            size="small"
                            onClick={(e) => {
                              e.stopPropagation();
                              removeNotification(notification.id);
                            }}
                            sx={{ padding: 0.5 }}
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                            {notification.message}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatTime(notification.timestamp)}
                          </Typography>
                          {!notification.read && (
                            <Chip
                              label={t('notifications.new')}
                              size="small"
                              color="primary"
                              variant="outlined"
                              sx={{ ml: 1, fontSize: '0.6rem', height: 20 }}
                            />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < notifications.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          )}
        </Box>
      </Paper>
    </Popover>
  );
};

export default NotificationPanel; 