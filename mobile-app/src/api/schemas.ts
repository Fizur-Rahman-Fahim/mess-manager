import { z } from 'zod';

const decimalish = z.union([z.string(), z.number()]).transform((value) => String(value));
const nullableDecimalish = z
  .union([z.string(), z.number(), z.null()])
  .transform((value) => (value === null ? null : String(value)));

export const userSchema = z.object({
  id: z.number(),
  mobile_number: z.string(),
  full_name: z.string(),
  is_active_member: z.boolean(),
  is_super_manager: z.boolean(),
  is_monthly_manager: z.boolean(),
  role: z.string(),
  date_joined: z.string(),
  profile_photo: z.string().nullable().optional().transform((value) => value ?? null),
});

export const loginResponseSchema = z.object({
  access: z.string(),
  refresh: z.string(),
  user: userSchema,
});

export const registerResponseSchema = z.object({
  message: z.string(),
  mobile_number: z.string(),
});

export const mealEntrySchema = z.object({
  id: z.number().nullable().optional().transform((value) => value ?? null),
  date: z.string(),
  breakfast: z.boolean(),
  lunch: z.boolean(),
  dinner: z.boolean(),
  total_meal_value: decimalish,
  can_edit: z.boolean(),
});

export const myMealsResponseSchema = z.object({
  month: z.string(),
  meals: z.array(mealEntrySchema),
});

export const mealSummaryMemberSchema = z.object({
  user_id: z.number(),
  full_name: z.string(),
  mobile_number: z.string(),
  breakfast_count: z.number(),
  lunch_count: z.number(),
  dinner_count: z.number(),
  total_meal_value: decimalish,
});

export const mealSummaryResponseSchema = z.object({
  month: z.string(),
  members: z.array(mealSummaryMemberSchema),
});

export const dailyMemberStatusSchema = z.object({
  user_id: z.number(),
  full_name: z.string(),
  mobile_number: z.string(),
  breakfast: z.boolean(),
  lunch: z.boolean(),
  dinner: z.boolean(),
});

export const dailySummaryDaySchema = z.object({
  date: z.string(),
  breakfast_on: z.number(),
  breakfast_off: z.number(),
  lunch_on: z.number(),
  lunch_off: z.number(),
  dinner_on: z.number(),
  dinner_off: z.number(),
  members: z.array(dailyMemberStatusSchema),
});

export const dailySummaryResponseSchema = z.object({
  month: z.string(),
  days: z.array(dailySummaryDaySchema),
});

export const fixedMealResponseSchema = z.object({
  month: z.string(),
  fixed_meal_count: decimalish,
});

export const depositSchema = z.object({
  id: z.number(),
  user: z.number(),
  user_name: z.string(),
  user_mobile: z.string(),
  amount: decimalish,
  date_claimed: z.string(),
  status: z.string(),
  status_display: z.string(),
  approved_by: z.number().nullable(),
  approved_at: z.string().nullable(),
  note: z.string().optional().default(''),
  created_at: z.string(),
});

export const myDepositsResponseSchema = z.object({
  month: z.string(),
  deposits: z.array(depositSchema),
});

export const pendingDepositsResponseSchema = z.object({
  deposits: z.array(depositSchema),
});

export const complaintSchema = z.object({
  id: z.number(),
  raised_by: z.number(),
  raised_by_name: z.string(),
  title: z.string(),
  description: z.string(),
  status: z.string(),
  handled_by: z.number().nullable(),
  handled_by_name: z.string().nullable().optional().transform((value) => value ?? null),
  created_at: z.string(),
  resolved_at: z.string().nullable(),
});

export const expenseSchema = z.object({
  id: z.number(),
  bazar_type: z.string(),
  bazar_type_display: z.string(),
  amount: decimalish,
  date: z.string(),
  description: z.string().optional().default(''),
  month: z.string(),
  added_by: z.number(),
  added_by_name: z.string(),
  receipt_image: z.string().nullable().optional().transform((value) => value ?? null),
  receipt_image_url: z.string().nullable().optional().transform((value) => value ?? null),
  created_at: z.string(),
});

export const expenseSummarySchema = z.object({
  month: z.string(),
  expenses: z.array(expenseSchema),
  boro_total: decimalish,
  choto_total: decimalish,
  total_bazar: decimalish,
  total_meal_count: decimalish,
  meal_rate: decimalish,
});

export const billRecordSchema = z.object({
  id: z.number(),
  user: z.number(),
  user_name: z.string(),
  user_mobile: z.string(),
  month: z.string(),
  seat_bill: decimalish,
  current_bill_share: decimalish,
  house_rent_share: decimalish,
  electricity_share: decimalish,
  meal_cost: decimalish,
  total_due: decimalish,
  total_deposit: decimalish,
  balance: decimalish,
});

export const billCycleSchema = z.object({
  month: z.string(),
  house_rent_total: decimalish,
  house_rent_paid: decimalish,
  electricity_bill_total: decimalish,
  electricity_bill_paid: decimalish,
  total_meal_count: decimalish,
  meal_rate: decimalish,
  updated_at: z.string(),
});

export const myBillResponseSchema = z.object({
  month: z.string(),
  bill: billRecordSchema.nullable(),
  cycle: billCycleSchema.nullable(),
  detail: z.string().optional(),
});

export const settingsSchema = z.object({
  seat_bill_default: decimalish,
  current_bill_default: decimalish,
  breakfast_meal_value: decimalish,
  lunch_meal_value: decimalish,
  dinner_meal_value: decimalish,
  meal_off_cutoff_time: z.string(),
  updated_by: z.number().nullable(),
  updated_at: z.string(),
});

export const managerAssignmentSchema = z.object({
  id: z.number(),
  user_id: z.number(),
  full_name: z.string(),
  mobile_number: z.string(),
  month: z.string(),
  is_active: z.boolean(),
  start_date: z.string(),
  end_date: z.union([z.string(), z.null()]),
});

export const managerAssignResponseSchema = z.object({
  active: managerAssignmentSchema.nullable(),
  history: z.array(managerAssignmentSchema),
});

export { decimalish, nullableDecimalish };
