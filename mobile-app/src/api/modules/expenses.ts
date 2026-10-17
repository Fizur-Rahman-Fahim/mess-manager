import { apiClient } from '../client';
import { parseApi } from '../parse';
import { expenseSchema, expenseSummarySchema } from '../schemas';

export const getBazarExpenses = async (month: string) => {
  const data = await apiClient.get<unknown>(`/expenses/bazar/?month=${month}`);
  return parseApi(expenseSummarySchema, data);
};

export const addBazarExpense = async (formData: FormData) => {
  const data = await apiClient.postFormData<unknown>('/expenses/bazar/', formData);
  return parseApi(expenseSchema, data);
};
