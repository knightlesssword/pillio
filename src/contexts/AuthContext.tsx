import React, { useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { AuthContext } from './auth-context';
import { User, LoginForm, RegisterForm } from '@/types';
import { toUser, type ApiUser } from '@/types';
import authApi from '@/lib/auth-api';
import { getErrorMessage } from '@/lib/api';

// Helper functions for storage management
const getStorage = (storageType: 'local' | 'session') => 
  storageType === 'local' ? localStorage : sessionStorage;

const getToken = (storageType: 'local' | 'session') => 
  getStorage(storageType).getItem('auth_token');

const setToken = (storageType: 'local' | 'session', token: string, refreshToken: string) => {
  const storage = getStorage(storageType);
  storage.setItem('auth_token', token);
  storage.setItem('refresh_token', refreshToken);
};

const clearAuthData = (storageType: 'local' | 'session') => {
  const storage = getStorage(storageType);
  storage.removeItem('auth_token');
  storage.removeItem('refresh_token');
  storage.removeItem('user');
};

// Check which storage has valid auth data
const getAuthStorageType = (): 'local' | 'session' | null => {
  if (localStorage.getItem('auth_token')) return 'local';
  if (sessionStorage.getItem('auth_token')) return 'session';
  return null;
};

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Refresh user data from API
  const refreshUser = useCallback(async (storageType: 'local' | 'session' = 'local') => {
    const token = getStorage(storageType).getItem('auth_token');
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const response = await authApi.getMe();
      const userData = toUser(response.data);
      setUser(userData);
      getStorage(storageType).setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // Token might be invalid, clear auth data from the correct storage
      clearAuthData(storageType);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check for existing auth token on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storageType = getAuthStorageType();
      if (storageType) {
        await refreshUser(storageType);
      } else {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [refreshUser]);

  const login = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const response = await authApi.login({
        email: data.email,
        password: data.password,
        remember_me: data.rememberMe,
      });

      const { access_token, refresh_token } = response.data;
      
      // Store tokens in localStorage (remember me) or sessionStorage (session only)
      const storageType = data.rememberMe ? 'local' : 'session';
      setToken(storageType, access_token, refresh_token);

      // Fetch user profile
      const userResponse = await authApi.getMe();
      const userData = toUser(userResponse.data);
      
      setUser(userData);
      getStorage(storageType).setItem('user', JSON.stringify(userData));
    } catch (error) {
      const message = getErrorMessage(error);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      const response = await authApi.register({
        email: data.email,
        password: data.password,
        first_name: data.name.split(' ')[0] || undefined,
        last_name: data.name.split(' ').slice(1).join(' ') || undefined,
      });

      const { access_token, refresh_token } = response.data;
      
      // Store tokens in sessionStorage by default for registration
      setToken('session', access_token, refresh_token);

      // Fetch user profile
      const userResponse = await authApi.getMe();
      const userData = toUser(userResponse.data);
      
      setUser(userData);
      sessionStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      const message = getErrorMessage(error);
      throw new Error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Ignore logout errors - we still want to clear local state
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      // Clear auth data from both storage types
      clearAuthData('local');
      clearAuthData('session');
    }
  };

  const forgotPassword = async (email: string) => {
    try {
      await authApi.forgotPassword({ email });
    } catch (error) {
      const message = getErrorMessage(error);
      throw new Error(message);
    }
  };

  const resetPassword = async (token: string, password: string) => {
    try {
      await authApi.resetPassword({
        token,
        new_password: password,
      });
    } catch (error) {
      const message = getErrorMessage(error);
      throw new Error(message);
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    if (!user) return;

    try {
      const updateData: Record<string, unknown> = {};
      
      if (data.name) {
        const nameParts = data.name.split(' ');
        updateData.first_name = nameParts[0];
        updateData.last_name = nameParts.slice(1).join(' ') || null;
      }
      if (data.email) {
        updateData.email = data.email;
      }
      if (data.phone) {
        updateData.phone = data.phone;
      }

      const response = await authApi.updateProfile(updateData);
      const updatedUser = toUser(response.data);
      
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    } catch (error) {
      const message = getErrorMessage(error);
      throw new Error(message);
    }
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
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
