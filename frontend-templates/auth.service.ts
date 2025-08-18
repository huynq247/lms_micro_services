// Authentication Service
import { apiClient } from './api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: 'student' | 'instructor' | 'admin';
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    isActive: boolean;
  };
}

export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login', credentials);
    return response.data;
  },

  // Register new user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/register', userData);
    return response.data;
  },

  // Get current user profile
  getProfile: async () => {
    const response = await apiClient.get('/api/auth/profile');
    return response.data;
  },

  // Update user profile
  updateProfile: async (userData: Partial<RegisterRequest>) => {
    const response = await apiClient.put('/api/auth/profile', userData);
    return response.data;
  },

  // Logout user
  logout: async () => {
    const response = await apiClient.post('/api/auth/logout');
    return response.data;
  },
};
