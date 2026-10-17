import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';
import { normalizeError } from '../utils/errorNormalizer';
import { AuthTokens } from '../utils/types';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

type RequestConfig = InternalAxiosRequestConfig & { _retry?: boolean };

type RefreshWaiter = {
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
};

class ApiClient {
  private axiosInstance: AxiosInstance;
  private isRefreshing = false;
  private refreshSubscribers: RefreshWaiter[] = [];
  private onSessionExpired: () => void = () => {};

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 45000,
    });

    this.setupInterceptors();
  }

  setOnSessionExpired(callback: () => void) {
    this.onSessionExpired = callback;
  }

  private notifyRefreshed(token: string) {
    this.refreshSubscribers.forEach((waiter) => waiter.resolve(token));
    this.refreshSubscribers = [];
  }

  private notifyRefreshFailed(error: unknown) {
    this.refreshSubscribers.forEach((waiter) => waiter.reject(error));
    this.refreshSubscribers = [];
  }

  private setupInterceptors() {
    this.axiosInstance.interceptors.request.use(async (config) => {
      const accessToken = await SecureStore.getItemAsync('accessToken');
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    });

    this.axiosInstance.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as RequestConfig | undefined;
        const requestUrl = originalRequest?.url ?? '';
        const skipRefresh =
          requestUrl.includes('/auth/login/') ||
          requestUrl.includes('/auth/register/') ||
          requestUrl.includes('/auth/refresh/');

        if (error.response?.status !== 401 || !originalRequest || originalRequest._retry || skipRefresh) {
          return Promise.reject(error);
        }

        originalRequest._retry = true;

        if (this.isRefreshing) {
          return new Promise((resolve, reject) => {
            this.refreshSubscribers.push({
              resolve: (token: string) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                resolve(this.axiosInstance(originalRequest));
              },
              reject,
            });
          });
        }

        this.isRefreshing = true;

        try {
          const existingRefresh = await SecureStore.getItemAsync('refreshToken');
          if (!existingRefresh) {
            throw new Error('No refresh token');
          }

          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: existingRefresh,
          });

          const newAccessToken = response.data.access as string;
          const newRefreshToken = (response.data.refresh as string | undefined) || existingRefresh;
          await this.storeTokens({ access: newAccessToken, refresh: newRefreshToken });

          this.notifyRefreshed(newAccessToken);
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return this.axiosInstance(originalRequest);
        } catch (refreshError) {
          this.notifyRefreshFailed(refreshError);
          await this.clearTokens();
          this.onSessionExpired();
          throw refreshError;
        } finally {
          this.isRefreshing = false;
        }
      }
    );
  }

  async storeTokens(tokens: AuthTokens): Promise<void> {
    await Promise.all([
      SecureStore.setItemAsync('accessToken', tokens.access),
      SecureStore.setItemAsync('refreshToken', tokens.refresh),
    ]);
  }

  async getStoredTokens(): Promise<AuthTokens | null> {
    const accessToken = await SecureStore.getItemAsync('accessToken');
    const refreshToken = await SecureStore.getItemAsync('refreshToken');

    if (!accessToken || !refreshToken) {
      return null;
    }

    return { access: accessToken, refresh: refreshToken };
  }

  async clearTokens(): Promise<void> {
    await Promise.all([
      SecureStore.deleteItemAsync('accessToken'),
      SecureStore.deleteItemAsync('refreshToken'),
    ]);
  }

  async get<T>(url: string): Promise<T> {
    try {
      const response = await this.axiosInstance.get<T>(url);
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    try {
      const response = await this.axiosInstance.post<T>(url, data);
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async patch<T>(url: string, data: unknown): Promise<T> {
    try {
      const response = await this.axiosInstance.patch<T>(url, data);
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }

  async postFormData<T>(url: string, formData: FormData): Promise<T> {
    try {
      const response = await this.axiosInstance.post<T>(url, formData);
      return response.data;
    } catch (error) {
      throw normalizeError(error);
    }
  }
}

export const apiClient = new ApiClient();
