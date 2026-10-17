import { apiClient } from '../client';
import { parseApi } from '../parse';
import { settingsSchema } from '../schemas';

export const getSettings = async () => {
  const data = await apiClient.get<unknown>('/settings/');
  return parseApi(settingsSchema, data);
};

export const patchSettings = async (payload: Record<string, string>) => {
  const data = await apiClient.patch<unknown>('/settings/', payload);
  return parseApi(settingsSchema, data);
};
