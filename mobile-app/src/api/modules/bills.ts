import { apiClient } from '../client';
import { parseApi } from '../parse';
import { billCycleSchema, myBillResponseSchema } from '../schemas';

export const getMyBill = async (month: string) => {
  const data = await apiClient.get<unknown>(`/bills/my-bill/?month=${month}`);
  return parseApi(myBillResponseSchema, data);
};

export const setHouseRent = async (payload: { month: string; total: string; paid?: string }) => {
  const data = await apiClient.post<unknown>('/bills/set-house-rent/', payload);
  return parseApi(billCycleSchema, data);
};

export const setElectricity = async (payload: { month: string; total: string; paid?: string }) => {
  const data = await apiClient.post<unknown>('/bills/set-electricity/', payload);
  return parseApi(billCycleSchema, data);
};

export const generateBills = async (month: string) => {
  const data = await apiClient.post<unknown>('/bills/generate/', { month });
  return parseApi(billCycleSchema, data);
};
