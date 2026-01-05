import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginForm, RegisterForm } from '@/types';
import api from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginForm) => Promise<void>;
  register: (data: RegisterForm) => Promise<void>;
  logout: () => void;
  forgotPassword: (email: string) => Promise<void>;
  resetPassword: (token: string, password: string) => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing auth token and validate
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          // In a real app, this would validate the token with the backend
          const savedUser = localStorage.getItem('user');
          if (savedUser) {
            setUser(JSON.parse(savedUser));
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user');
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      // Mock login for demo - replace with actual API call
      // const response = await api.post('/auth/login', data);
      const mockUser: User = {
        id: '1',
        email: data.email,
        name: 'John Doe',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      setUser(mockUser);
      localStorage.setItem('user', JSON.stringify(mockUser));
      api.setToken('mock_token_' + Date.now());
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      // Mock registration for demo
      const mockUser: User = {
        id: '1',
        email: data.email,
        name: data.name,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      
      setUser(mockUser);
      localStorage.setItem('user', JSON.stringify(mockUser));
      api.setToken('mock_token_' + Date.now());
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    api.setToken(null);
  };

  const forgotPassword = async (email: string) => {
    // Mock forgot password
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Password reset email sent to:', email);
  };

  const resetPassword = async (token: string, password: string) => {
    // Mock reset password
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Password reset with token:', token);
  };

  const updateProfile = async (data: Partial<User>) => {
    if (!user) return;
    
    const updatedUser = { ...user, ...data, updatedAt: new Date().toISOString() };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        forgotPassword,
        resetPassword,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
