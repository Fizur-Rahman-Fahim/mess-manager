import { create } from 'zustand';
import {
  approveUser,
  getMe,
  getPendingApprovals,
  login as loginRequest,
  register as registerRequest,
} from '../api/modules/auth';
import { apiClient } from '../api/client';
import { queryClient } from '../api/queryClient';
import { isPendingApprovalError, NormalizedError } from '../utils/errorNormalizer';
import { User } from '../utils/types';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  /** true only while the initial session check runs at app start */
  isBootstrapping: boolean;
  /** true while a login/register request is in flight (does NOT unmount screens) */
  isLoading: boolean;
  showPendingApproval: boolean;
  pendingMobile: string | null;
  error: NormalizedError | null;
  /** set when bootstrap failed because of network/server problems (tokens are kept) */
  bootstrapError: NormalizedError | null;

  login: (mobileNumber: string, password: string) => Promise<void>;
  register: (payload: {
    mobile_number: string;
    full_name: string;
    password1: string;
    password2: string;
  }) => Promise<void>;
  bootstrap: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUserProfile: () => Promise<void>;
  clearError: () => void;
  dismissPending: () => void;

  isManager: () => boolean;
  isSuperManager: () => boolean;
}

const isRetryable = (error: NormalizedError) => error.status === 0 || error.status >= 500;

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isBootstrapping: true,
  isLoading: false,
  showPendingApproval: false,
  pendingMobile: null,
  error: null,
  bootstrapError: null,

  login: async (mobileNumber, password) => {
    set({ isLoading: true, error: null, showPendingApproval: false });
    try {
      const response = await loginRequest(mobileNumber, password);
      await apiClient.storeTokens({ access: response.access, refresh: response.refresh });
      queryClient.clear();
      set({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
        showPendingApproval: false,
        pendingMobile: null,
      });
    } catch (error) {
      const normalized = error as NormalizedError;
      const pending = isPendingApprovalError(normalized);
      set({
        error: pending ? null : normalized,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        showPendingApproval: pending,
        pendingMobile: pending ? mobileNumber : null,
      });
      throw error;
    }
  },

  register: async (payload) => {
    set({ isLoading: true, error: null });
    try {
      const response = await registerRequest(payload);
      set({
        isLoading: false,
        isAuthenticated: false,
        user: null,
        showPendingApproval: true,
        pendingMobile: response.mobile_number ?? payload.mobile_number,
        error: null,
      });
    } catch (error) {
      set({ error: error as NormalizedError, isLoading: false });
      throw error;
    }
  },

  bootstrap: async () => {
    set({ isBootstrapping: true, bootstrapError: null });
    try {
      const tokens = await apiClient.getStoredTokens();
      if (!tokens) {
        set({ isBootstrapping: false, isAuthenticated: false, user: null });
        return;
      }

      const user = await getMe();
      set({
        user,
        isAuthenticated: true,
        isBootstrapping: false,
        showPendingApproval: false,
      });
    } catch (error) {
      const normalized = error as NormalizedError;
      if (isRetryable(normalized)) {
        // Do not log the user out because of a bad connection — keep tokens and offer retry.
        set({ isBootstrapping: false, bootstrapError: normalized });
        return;
      }
      await apiClient.clearTokens();
      set({
        isAuthenticated: false,
        user: null,
        isBootstrapping: false,
        showPendingApproval: isPendingApprovalError(normalized),
      });
    }
  },

  logout: async () => {
    await apiClient.clearTokens();
    queryClient.clear();
    set({
      user: null,
      isAuthenticated: false,
      showPendingApproval: false,
      pendingMobile: null,
      error: null,
      bootstrapError: null,
    });
  },

  refreshUserProfile: async () => {
    try {
      const user = await getMe();
      set({ user, isAuthenticated: true });
    } catch (error) {
      set({ error: error as NormalizedError });
    }
  },

  clearError: () => set({ error: null }),
  dismissPending: () => set({ showPendingApproval: false, pendingMobile: null, error: null }),

  isManager: () => {
    const { user } = get();
    return Boolean(user?.is_monthly_manager || user?.is_super_manager);
  },
  isSuperManager: () => Boolean(get().user?.is_super_manager),
}));

// Refresh token expired/invalid -> clear session and return to login.
apiClient.setOnSessionExpired(() => {
  queryClient.clear();
  useAuthStore.setState({
    user: null,
    isAuthenticated: false,
    showPendingApproval: false,
    pendingMobile: null,
  });
});

export { approveUser, getPendingApprovals };
