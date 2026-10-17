import { apiClient } from '../client';
import { parseApi } from '../parse';
import {
  dailySummaryResponseSchema,
  fixedMealResponseSchema,
  mealEntrySchema,
  mealSummaryResponseSchema,
  myMealsResponseSchema,
} from '../schemas';

export const getMyMeals = async (month: string) => {
  const data = await apiClient.get<unknown>(`/meals/my-meals/?month=${month}`);
  return parseApi(myMealsResponseSchema, data);
};

export const toggleMeal = async (payload: {
  date: string;
  breakfast: boolean;
  lunch: boolean;
  dinner: boolean;
}) => {
  const data = await apiClient.post<unknown>('/meals/toggle/', payload);
  return parseApi(mealEntrySchema, data);
};

export const getMealSummary = async (month: string) => {
  const data = await apiClient.get<unknown>(`/meals/summary/?month=${month}`);
  return parseApi(mealSummaryResponseSchema, data);
};

export const getDailyMealSummary = async (month: string) => {
  const data = await apiClient.get<unknown>(`/meals/daily-summary/?month=${month}`);
  return parseApi(dailySummaryResponseSchema, data);
};

export const getFixedMeals = async (month: string) => {
  const data = await apiClient.get<unknown>(`/meals/fixed/?month=${month}`);
  return parseApi(fixedMealResponseSchema, data);
};

export const setFixedMeals = async (month: string, fixed_meal_count: number) => {
  const data = await apiClient.post<unknown>('/meals/fixed/', { month, fixed_meal_count });
  return parseApi(fixedMealResponseSchema, data);
};
