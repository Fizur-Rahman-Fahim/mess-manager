import { apiClient } from '../client';
import { parseApi } from '../parse';
import { depositSchema, myDepositsResponseSchema, pendingDepositsResponseSchema } from '../schemas';

export const getMyDeposits = async (month: string) => {
  const data = await apiClient.get<unknown>(`/deposits/my-deposits/?month=${month}`);
  return parseApi(myDepositsResponseSchema, data);
};

export const claimDeposit = async (payload: {
  amount: string;
  date_claimed: string;
  note?: string;
}) => {
  const data = await apiClient.post<unknown>('/deposits/claim/', payload);
  return parseApi(depositSchema, data);
};

export const getPendingDeposits = async () => {
  const data = await apiClient.get<unknown>('/deposits/pending/');
  return parseApi(pendingDepositsResponseSchema, data);
};

export const approveDeposit = async (depositId: number) => {
  const data = await apiClient.post<unknown>(`/deposits/${depositId}/approve/`);
  return parseApi(depositSchema, data);
};

export const rejectDeposit = async (depositId: number) => {
  const data = await apiClient.post<unknown>(`/deposits/${depositId}/reject/`);
  return parseApi(depositSchema, data);
};
