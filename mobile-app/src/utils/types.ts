export type UserRole = 'Member' | 'Monthly Manager' | 'Super Manager';

export interface User {
  id: number;
  mobile_number: string;
  full_name: string;
  is_active_member: boolean;
  is_super_manager: boolean;
  is_monthly_manager: boolean;
  role: UserRole | string;
  date_joined: string;
  profile_photo: string | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

export interface RegisterResponse {
  message: string;
  mobile_number: string;
}

export interface MealEntry {
  id: number | null;
  date: string;
  breakfast: boolean;
  lunch: boolean;
  dinner: boolean;
  total_meal_value: string;
  can_edit: boolean;
}

export interface Deposit {
  id: number;
  user: number;
  user_name: string;
  user_mobile: string;
  amount: string;
  date_claimed: string;
  status: string;
  status_display: string;
  approved_by: number | null;
  approved_at: string | null;
  note: string;
  created_at: string;
}

export interface Complaint {
  id: number;
  raised_by: number;
  raised_by_name: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'resolved' | string;
  handled_by: number | null;
  handled_by_name: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface Expense {
  id: number;
  bazar_type: 'boro' | 'choto' | string;
  bazar_type_display: string;
  amount: string;
  date: string;
  description: string;
  month: string;
  added_by: number;
  added_by_name: string;
  receipt_image: string | null;
  receipt_image_url: string | null;
  created_at: string;
}

export interface BillRecord {
  id: number;
  user: number;
  user_name: string;
  user_mobile: string;
  month: string;
  seat_bill: string;
  current_bill_share: string;
  house_rent_share: string;
  electricity_share: string;
  meal_cost: string;
  total_due: string;
  total_deposit: string;
  balance: string;
}

export interface BillCycle {
  month: string;
  house_rent_total: string;
  house_rent_paid: string;
  electricity_bill_total: string;
  electricity_bill_paid: string;
  total_meal_count: string;
  meal_rate: string;
  updated_at: string;
}

export interface MessSettings {
  seat_bill_default: string;
  current_bill_default: string;
  breakfast_meal_value: string;
  lunch_meal_value: string;
  dinner_meal_value: string;
  meal_off_cutoff_time: string;
  updated_by: number | null;
  updated_at: string;
}

export interface ManagerAssignment {
  id: number;
  user_id: number;
  full_name: string;
  mobile_number: string;
  month: string;
  is_active: boolean;
  start_date: string;
  end_date: string | null;
}

export interface ApiError {
  status: number;
  message: string;
  errorCode?: string;
  userMessage: string;
  fieldErrors?: Record<string, string[]>;
}
