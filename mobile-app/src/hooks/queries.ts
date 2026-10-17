import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as mealsApi from '../api/modules/meals';
import * as depositsApi from '../api/modules/deposits';
import * as complaintsApi from '../api/modules/complaints';
import * as expensesApi from '../api/modules/expenses';
import * as billsApi from '../api/modules/bills';
import * as settingsApi from '../api/modules/settings';
import * as managerApi from '../api/modules/manager';
import * as authApi from '../api/modules/auth';

export const queryKeys = {
  myMeals: (month: string) => ['meals', 'mine', month] as const,
  mealSummary: (month: string) => ['meals', 'summary', month] as const,
  dailySummary: (month: string) => ['meals', 'daily', month] as const,
  fixedMeals: (month: string) => ['meals', 'fixed', month] as const,
  myDeposits: (month: string) => ['deposits', 'mine', month] as const,
  pendingDeposits: ['deposits', 'pending'] as const,
  myComplaints: ['complaints', 'mine'] as const,
  allComplaints: ['complaints', 'all'] as const,
  expenses: (month: string) => ['expenses', month] as const,
  myBill: (month: string) => ['bills', 'mine', month] as const,
  settings: ['settings'] as const,
  managerAssign: ['manager', 'assign'] as const,
  pendingUsers: ['users', 'pending'] as const,
};

export const useMyMeals = (month: string) =>
  useQuery({ queryKey: queryKeys.myMeals(month), queryFn: () => mealsApi.getMyMeals(month) });

export const useMealSummary = (month: string, enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.mealSummary(month),
    queryFn: () => mealsApi.getMealSummary(month),
    enabled,
  });

export const useDailyMealSummary = (month: string, enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.dailySummary(month),
    queryFn: () => mealsApi.getDailyMealSummary(month),
    enabled,
  });

export const useFixedMeals = (month: string, enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.fixedMeals(month),
    queryFn: () => mealsApi.getFixedMeals(month),
    enabled,
  });

export const useToggleMeal = (month: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: mealsApi.toggleMeal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.myMeals(month) });
      queryClient.invalidateQueries({ queryKey: ['meals'] });
    },
  });
};

export const useSetFixedMeals = (month: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (count: number) => mealsApi.setFixedMeals(month, count),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.fixedMeals(month) }),
  });
};

export const useMyDeposits = (month: string) =>
  useQuery({ queryKey: queryKeys.myDeposits(month), queryFn: () => depositsApi.getMyDeposits(month) });

export const useClaimDeposit = (month: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: depositsApi.claimDeposit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.myDeposits(month) });
      queryClient.invalidateQueries({ queryKey: queryKeys.pendingDeposits });
    },
  });
};

export const usePendingDeposits = (enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.pendingDeposits,
    queryFn: depositsApi.getPendingDeposits,
    enabled,
  });

export const useDepositReview = () => {
  const queryClient = useQueryClient();
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.pendingDeposits });
    queryClient.invalidateQueries({ queryKey: ['deposits'] });
  };
  return {
    approve: useMutation({ mutationFn: depositsApi.approveDeposit, onSuccess: invalidate }),
    reject: useMutation({ mutationFn: depositsApi.rejectDeposit, onSuccess: invalidate }),
  };
};

export const useMyComplaints = () =>
  useQuery({ queryKey: queryKeys.myComplaints, queryFn: complaintsApi.getMyComplaints });

export const useCreateComplaint = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: complaintsApi.createComplaint,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.myComplaints }),
  });
};

export const useAllComplaints = (enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.allComplaints,
    queryFn: complaintsApi.getAllComplaints,
    enabled,
  });

export const useUpdateComplaintStatus = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: 'pending' | 'in_progress' | 'resolved' }) =>
      complaintsApi.updateComplaintStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.allComplaints });
      queryClient.invalidateQueries({ queryKey: queryKeys.myComplaints });
    },
  });
};

export const useBazarExpenses = (month: string, enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.expenses(month),
    queryFn: () => expensesApi.getBazarExpenses(month),
    enabled,
  });

export const useAddBazarExpense = (month: string) => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: expensesApi.addBazarExpense,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.expenses(month) }),
  });
};

export const useMyBill = (month: string) =>
  useQuery({ queryKey: queryKeys.myBill(month), queryFn: () => billsApi.getMyBill(month) });

export const useBillActions = (month: string) => {
  const queryClient = useQueryClient();
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.myBill(month) });
  };
  return {
    setHouseRent: useMutation({ mutationFn: billsApi.setHouseRent, onSuccess: invalidate }),
    setElectricity: useMutation({ mutationFn: billsApi.setElectricity, onSuccess: invalidate }),
    generate: useMutation({ mutationFn: () => billsApi.generateBills(month), onSuccess: invalidate }),
  };
};

export const useSettings = () =>
  useQuery({ queryKey: queryKeys.settings, queryFn: settingsApi.getSettings });

export const usePatchSettings = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.patchSettings,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.settings }),
  });
};

export const useManagerAssignments = (enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.managerAssign,
    queryFn: managerApi.getManagerAssignments,
    enabled,
  });

export const useAssignManager = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: managerApi.assignManager,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.managerAssign }),
  });
};

export const usePendingUsers = (enabled: boolean) =>
  useQuery({
    queryKey: queryKeys.pendingUsers,
    queryFn: authApi.getPendingApprovals,
    enabled,
  });

export const useApproveUser = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: authApi.approveUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.pendingUsers }),
  });
};
