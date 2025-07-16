import React, { createContext, useContext, ReactNode, useCallback } from 'react';
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 10000,
});

interface FetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  params?: any;
  body?: any;
}

interface ApiContextType {
  fetchData: (endpoint: string, options?: FetchOptions) => Promise<any>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

interface ApiProviderProps {
  children: ReactNode;
}

export const ApiProvider: React.FC<ApiProviderProps> = ({ children }) => {
  const fetchData = useCallback(async (endpoint: string, options: FetchOptions = {}) => {
    const { method = 'GET', params, body } = options;
    try {
      const response = await api.request({
        url: endpoint,
        method,
        params,
        data: body,
      });
      return response.data;
    } catch (error) {
      console.error(`API call to ${endpoint} failed:`, error);
      throw error;
    }
  }, []);

  const value = { fetchData };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
}; 