import { apiClient } from '../client';
import { parseApi } from '../parse';
import { loginResponseSchema, registerResponseSchema, userSchema } from '../schemas';
import { LoginResponse, RegisterResponse, User } from '../../utils/types';

export const login = async (mobile_number: string, password: string): Promise<LoginResponse> => {
  const data = await apiClient.post<unknown>('/auth/login/', { mobile_number, password });
  return parseApi(loginResponseSchema, data);
};

export const register = async (payload: {
  mobile_number: string;
  full_name: string;
  password1: string;
  password2: string;
}): Promise<RegisterResponse> => {
  const data = await apiClient.post<unknown>('/auth/register/', payload);
  return parseApi(registerResponseSchema, data);
};

export const getMe = async (): Promise<User> => {
  const data = await apiClient.get<unknown>('/users/me/');
  return parseApi(userSchema, data);
};

export const getPendingApprovals = async (): Promise<User[]> => {
  const data = await apiClient.get<unknown>('/users/pending-approval/');
  return parseApi(userSchema.array(), data);
};

export const approveUser = async (userId: number): Promise<User> => {
  const data = await apiClient.post<unknown>(`/users/${userId}/approve/`);
  return parseApi(userSchema, data);
};
