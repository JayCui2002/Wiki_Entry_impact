import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// 支持的语言类型
export type Language = 'zh' | 'en';

// 语言配置接口
interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

// 中文翻译
const zhTranslations = {
  // 通用
  'common.loading': '加载中...',
  'common.error': '错误',
  'common.success': '成功',
  'common.cancel': '取消',
  'common.confirm': '确认',
  'common.save': '保存',
  'common.delete': '删除',
  'common.edit': '编辑',
  'common.search': '搜索',
  'common.filter': '筛选',
  'common.export': '导出',
  'common.refresh': '刷新',
  'common.columns': '列',
  'common.density': '密度',
  
  // 导航菜单
  'nav.dashboard': '仪表板',
  'nav.contributors': '贡献者',
  'nav.analytics': '分析',
  'nav.comparison': '对比',
  'nav.wikiAnalysis': 'Wiki分析',
  'nav.analysisHistory': '分析历史',
  'nav.settings': '设置',
  
  // Header
  'header.title': 'Wiki Entry Impact Dashboard',
  'header.notifications': '通知',
  'header.toggleDarkMode': '切换到深色模式',
  'header.toggleLightMode': '切换到浅色模式',
  'header.settings': '设置',
  
  // 设置页面
  'settings.title': '设置',
  'settings.appearance': '外观设置',
  'settings.language': '语言设置',
  'settings.notifications': '通知设置',
  'settings.data': '数据设置',
  'settings.darkMode': '深色模式',
  'settings.darkModeDesc': '切换到深色主题以减少眼部疲劳',
  'settings.interfaceLanguage': '界面语言',
  'settings.currentLanguage': '当前: 简体中文',
  'settings.analysisNotification': '分析完成通知',
  'settings.analysisNotificationDesc': '当Wikipedia分析完成时显示通知',
  'settings.systemNotification': '系统更新通知',
  'settings.systemNotificationDesc': '当有新功能或更新时显示通知',
  'settings.cacheManagement': '缓存管理',
  'settings.cacheManagementDesc': '清除应用缓存以释放存储空间',
  'settings.dataExport': '数据导出',
  'settings.dataExportDesc': '导出分析数据和贡献者信息',
  'settings.version': 'Wiki Entry Impact Assessment System v1.0.0',
  'settings.copyright': '© 2024 开发团队. 保留所有权利.',
  
  // 语言选项
  'language.chinese': '简体中文',
  'language.english': 'English',
  
  // Dashboard
  'dashboard.title': '仪表板',
  'dashboard.overview': '概览',
  'dashboard.totalContributors': '总贡献者',
  'dashboard.activeContributors': '活跃贡献者',
  'dashboard.averageImpact': '平均影响分',
  'dashboard.topContributors': '顶级贡献者',
  'dashboard.fetchError': '获取仪表板数据失败',
  
  // Contributors
  'contributors.title': '贡献者',
  'contributors.list': '贡献者列表',
  'contributors.name': '姓名',
  'contributors.displayName': '显示名称',
  'contributors.wikipediaUsername': 'Wikipedia用户名',
  'contributors.edits': '编辑次数',
  'contributors.impact': '影响分',
  'contributors.type': '类型',
  'contributors.language': '语言',
  'contributors.actions': '操作',
  'contributors.viewDetails': '查看详情',
  'contributors.noData': '暂无数据',
  'contributors.fetchError': '获取贡献者数据失败',
  'contributors.status': '状态',
  
  // Analytics
  'analytics.title': '分析',
  'analytics.statistics': '统计数据',
  'analytics.charts': '图表',
  
  // Comparison
  'comparison.title': '对比',
  'comparison.selectContributors': '选择贡献者进行对比',
  
  // Wiki Analysis
  'wikiAnalysis.title': 'Wiki分析',
  'wikiAnalysis.description': '输入Wikipedia页面的完整URL，获取其历史记录，分析贡献者并计算其影响分数。',
  'wikiAnalysis.urlLabel': 'Wikipedia页面URL',
  'wikiAnalysis.urlPlaceholder': '例如: https://en.wikipedia.org/wiki/Example',
  'wikiAnalysis.startButton': '开始分析',
  'wikiAnalysis.successMessage': '分析已成功启动',
  'wikiAnalysis.errorMessage': '启动分析失败，请检查URL并重试',
  'wikiAnalysis.analyze': '开始分析',
  'wikiAnalysis.enterUrl': '输入Wikipedia URL',
  
  // Analysis History
  'analysisHistory.title': '分析历史',
  'analysisHistory.description': '查看所有Wikipedia页面分析，并探索每个会话中发现的贡献者。',
  'analysisHistory.noSessions': '未找到分析会话。请先分析一个Wikipedia页面！',
  'analysisHistory.contributors': '贡献者',
  'analysisHistory.revisions': '修订版本',
  'analysisHistory.started': '开始时间',
  'analysisHistory.viewContributors': '查看贡献者',
  'analysisHistory.deleteSession': '删除',
  'analysisHistory.contributorsIn': '贡献者列表',
  'analysisHistory.loadError': '加载分析历史失败',
  'analysisHistory.recentAnalysis': '最近分析',
  'analysisHistory.date': '日期',
  'analysisHistory.article': '文章',
  'analysisHistory.status': '状态',
};

// 英文翻译
const enTranslations = {
  // Common
  'common.loading': 'Loading...',
  'common.error': 'Error',
  'common.success': 'Success',
  'common.cancel': 'Cancel',
  'common.confirm': 'Confirm',
  'common.save': 'Save',
  'common.delete': 'Delete',
  'common.edit': 'Edit',
  'common.search': 'Search',
  'common.filter': 'Filter',
  'common.export': 'Export',
  'common.refresh': 'Refresh',
  'common.columns': 'Columns',
  'common.density': 'Density',
  
  // Navigation
  'nav.dashboard': 'Dashboard',
  'nav.contributors': 'Contributors',
  'nav.analytics': 'Analytics',
  'nav.comparison': 'Comparison',
  'nav.wikiAnalysis': 'Wiki Analysis',
  'nav.analysisHistory': 'Analysis History',
  'nav.settings': 'Settings',
  
  // Header
  'header.title': 'Wiki Entry Impact Dashboard',
  'header.notifications': 'Notifications',
  'header.toggleDarkMode': 'Switch to Dark Mode',
  'header.toggleLightMode': 'Switch to Light Mode',
  'header.settings': 'Settings',
  
  // Settings
  'settings.title': 'Settings',
  'settings.appearance': 'Appearance',
  'settings.language': 'Language Settings',
  'settings.notifications': 'Notifications',
  'settings.data': 'Data Settings',
  'settings.darkMode': 'Dark Mode',
  'settings.darkModeDesc': 'Switch to dark theme to reduce eye strain',
  'settings.interfaceLanguage': 'Interface Language',
  'settings.currentLanguage': 'Current: English',
  'settings.analysisNotification': 'Analysis Completion Notifications',
  'settings.analysisNotificationDesc': 'Show notifications when Wikipedia analysis is completed',
  'settings.systemNotification': 'System Update Notifications',
  'settings.systemNotificationDesc': 'Show notifications when new features or updates are available',
  'settings.cacheManagement': 'Cache Management',
  'settings.cacheManagementDesc': 'Clear application cache to free up storage space',
  'settings.dataExport': 'Data Export',
  'settings.dataExportDesc': 'Export analysis data and contributor information',
  'settings.version': 'Wiki Entry Impact Assessment System v1.0.0',
  'settings.copyright': '© 2024 Development Team. All rights reserved.',
  
  // Language options
  'language.chinese': '简体中文',
  'language.english': 'English',
  
  // Dashboard
  'dashboard.title': 'Dashboard',
  'dashboard.overview': 'Overview',
  'dashboard.totalContributors': 'Total Contributors',
  'dashboard.activeContributors': 'Active Contributors',
  'dashboard.averageImpact': 'Average Impact',
  'dashboard.topContributors': 'Top Contributors',
  'dashboard.fetchError': 'Failed to fetch dashboard data',
  
  // Contributors
  'contributors.title': 'Contributors',
  'contributors.list': 'Contributors List',
  'contributors.name': 'Name',
  'contributors.displayName': 'Display Name',
  'contributors.wikipediaUsername': 'Wikipedia Username',
  'contributors.edits': 'Edits',
  'contributors.impact': 'Impact Score',
  'contributors.type': 'Type',
  'contributors.language': 'Language',
  'contributors.actions': 'Actions',
  'contributors.viewDetails': 'View Details',
  'contributors.noData': 'No data available',
  'contributors.fetchError': 'Failed to fetch contributors data',
  'contributors.status': 'Status',
  
  // Analytics
  'analytics.title': 'Analytics',
  'analytics.statistics': 'Statistics',
  'analytics.charts': 'Charts',
  
  // Comparison
  'comparison.title': 'Comparison',
  'comparison.selectContributors': 'Select contributors to compare',
  
  // Wiki Analysis
  'wikiAnalysis.title': 'Wiki Analysis',
  'wikiAnalysis.description': 'Enter the full URL of a Wikipedia page to fetch its history, analyze its contributors, and calculate their impact scores.',
  'wikiAnalysis.urlLabel': 'Wikipedia Page URL',
  'wikiAnalysis.urlPlaceholder': 'e.g., https://en.wikipedia.org/wiki/Example',
  'wikiAnalysis.startButton': 'Start Analysis',
  'wikiAnalysis.successMessage': 'Analysis has been successfully started',
  'wikiAnalysis.errorMessage': 'Failed to start analysis. Please check the URL and try again.',
  'wikiAnalysis.analyze': 'Start Analysis',
  'wikiAnalysis.enterUrl': 'Enter Wikipedia URL',
  
  // Analysis History
  'analysisHistory.title': 'Analysis History',
  'analysisHistory.description': 'View all your Wikipedia page analyses and explore the contributors found in each session.',
  'analysisHistory.noSessions': 'No analysis sessions found. Start by analyzing a Wikipedia page!',
  'analysisHistory.contributors': 'Contributors',
  'analysisHistory.revisions': 'Revisions',
  'analysisHistory.started': 'Started',
  'analysisHistory.viewContributors': 'View Contributors',
  'analysisHistory.deleteSession': 'Delete',
  'analysisHistory.contributorsIn': 'Contributors in',
  'analysisHistory.loadError': 'Failed to load analysis history',
  'analysisHistory.recentAnalysis': 'Recent Analysis',
  'analysisHistory.date': 'Date',
  'analysisHistory.article': 'Article',
  'analysisHistory.status': 'Status',
};

const translations = {
  zh: zhTranslations,
  en: enTranslations,
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

interface LanguageProviderProps {
  children: ReactNode;
}

export const LanguageProvider: React.FC<LanguageProviderProps> = ({ children }) => {
  // 从localStorage读取保存的语言偏好，默认为中文
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('language');
    return (saved as Language) || 'zh';
  });

  // 保存语言偏好到localStorage
  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  // 翻译函数
  const t = (key: string): string => {
    return (translations[language] as Record<string, string>)[key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}; 