import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';

// 通知类型定义
export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  timestamp: Date;
  read: boolean;
  autoHide?: boolean;
  duration?: number; // 自动隐藏时间（毫秒）
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => string;
  removeNotification: (id: string) => void;
  markAsRead: (id: string) => void;
  markAllAsRead: () => void;
  clearAll: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  // 生成唯一ID
  const generateId = () => {
    return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  // 添加通知
  const addNotification = useCallback((notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>): string => {
    const id = generateId();
    const newNotification: Notification = {
      ...notificationData,
      id,
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => [newNotification, ...prev]);

    // 自动隐藏通知（如果设置了autoHide）
    if (notificationData.autoHide) {
      const duration = notificationData.duration || 5000; // 默认5秒
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  }, []);

  // 移除通知
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // 标记为已读
  const markAsRead = useCallback((id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id 
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  // 标记所有为已读
  const markAllAsRead = useCallback(() => {
    setNotifications(prev => 
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  // 清除所有通知
  const clearAll = useCallback(() => {
    setNotifications([]);
  }, []);

  // 计算未读数量
  const unreadCount = notifications.filter(notification => !notification.read).length;

  const value = {
    notifications,
    unreadCount,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}; 