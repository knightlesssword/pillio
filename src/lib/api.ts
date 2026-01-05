// API Client wrapper for FastAPI backend
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface RequestConfig extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
    this.token = localStorage.getItem('auth_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private buildUrl(endpoint: string, params?: Record<string, string | number | boolean>): string {
    const url = new URL(`${this.baseUrl}${endpoint}`);
    
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    return url.toString();
  }

  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<ApiResponse<T>> {
    const { params, ...fetchConfig } = config;
    const url = this.buildUrl(endpoint, params);

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        headers: {
          ...this.getHeaders(),
          ...fetchConfig.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'An error occurred');
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    const response = await this.request<T>(endpoint, { method: 'GET', params });
    return response.data;
  }

  async post<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
    return response.data;
  }

  async put<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
    return response.data;
  }

  async patch<T>(endpoint: string, body?: unknown): Promise<T> {
    const response = await this.request<T>(endpoint, {
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
    return response.data;
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.request<T>(endpoint, { method: 'DELETE' });
    return response.data;
  }

  async uploadFile<T>(endpoint: string, file: File, fieldName: string = 'file'): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);

    const headers: HeadersInit = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Upload failed');
    }

    return data;
  }
}

export const api = new ApiClient(API_BASE_URL);

export default api;
