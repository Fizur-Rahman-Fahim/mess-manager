import { apiClient } from '../client';
import { parseApi } from '../parse';
import { managerAssignResponseSchema, managerAssignmentSchema } from '../schemas';

export const getManagerAssignments = async () => {
  const data = await apiClient.get<unknown>('/manager/assign/');
  return parseApi(managerAssignResponseSchema, data);
};

export const assignManager = async (payload: { user_id: number; month: string }) => {
  const data = await apiClient.post<unknown>('/manager/assign/', payload);
  return parseApi(managerAssignmentSchema, data);
};
