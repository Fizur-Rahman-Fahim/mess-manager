import { AxiosError, isAxiosError } from 'axios';

export interface NormalizedError {
  status: number;
  message: string;
  errorCode?: string;
  userMessage: string;
  fieldErrors?: Record<string, string[]>;
  retryAfterSeconds?: number;
}

export const isNetworkError = (error: NormalizedError): boolean => error.status === 0;

export const isAuthError = (error: NormalizedError): boolean => error.status === 401;

export const isForbiddenError = (error: NormalizedError): boolean => error.status === 403;

export const isPendingApprovalError = (error: NormalizedError): boolean =>
  error.errorCode === 'PENDING_APPROVAL' || /pending approval/i.test(error.message);

export const isNotFoundError = (error: NormalizedError): boolean => error.status === 404;

export const isRateLimitError = (error: NormalizedError): boolean => error.status === 429;

export const isValidationError = (error: NormalizedError): boolean => error.status === 400;

const asStringArray = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map((item) => (typeof item === 'string' ? item : JSON.stringify(item)));
  }
  if (typeof value === 'string') {
    return [value];
  }
  return [];
};

const extractDetail = (data: unknown): string => {
  if (!data || typeof data !== 'object') {
    return '';
  }
  const record = data as Record<string, unknown>;
  const detail = record.detail;
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === 'string') {
          return item;
        }
        if (item && typeof item === 'object' && 'string' in item) {
          return String((item as { string: unknown }).string);
        }
        return JSON.stringify(item);
      })
      .join(' ');
  }
  if (Array.isArray(record.non_field_errors)) {
    return asStringArray(record.non_field_errors).join(' ');
  }
  return typeof record.message === 'string' ? record.message : '';
};

const extractFieldErrors = (data: unknown): Record<string, string[]> | undefined => {
  if (!data || typeof data !== 'object') {
    return undefined;
  }
  const record = data as Record<string, unknown>;
  const skip = new Set(['detail', 'message', 'errorCode', 'userMessage', 'status']);
  const fieldErrors: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(record)) {
    if (skip.has(key)) {
      continue;
    }
    const messages = asStringArray(value);
    if (messages.length) {
      fieldErrors[key] = messages;
    }
  }
  return Object.keys(fieldErrors).length ? fieldErrors : undefined;
};

const parseRetryAfter = (error: AxiosError): number | undefined => {
  const header = error.response?.headers?.['retry-after'] ?? error.response?.headers?.['Retry-After'];
  if (!header) {
    return undefined;
  }
  const seconds = Number(header);
  return Number.isFinite(seconds) ? seconds : undefined;
};

export const normalizeError = (error: unknown): NormalizedError => {
  if (isAxiosError(error)) {
    const axiosError = error as AxiosError;
    const status = axiosError.response?.status || 0;
    const data = axiosError.response?.data;
    const detail = extractDetail(data);
    const fieldErrors = extractFieldErrors(data);

    if (status === 400) {
      return {
        status,
        message: detail || 'Validation error',
        errorCode: 'VALIDATION',
        userMessage: detail || 'Please check your input and try again',
        fieldErrors,
      };
    }

    if (status === 401) {
      return {
        status,
        message: detail || 'Unauthorized',
        errorCode: 'UNAUTHORIZED',
        userMessage: 'Your session has expired. Please login again.',
      };
    }

    if (status === 403) {
      const pending = /pending approval/i.test(detail);
      return {
        status,
        message: detail || 'Forbidden',
        errorCode: pending ? 'PENDING_APPROVAL' : 'FORBIDDEN',
        userMessage:
          detail ||
          (pending
            ? 'Your account is pending approval.'
            : 'You do not have permission to perform this action.'),
      };
    }

    if (status === 404) {
      return {
        status,
        message: detail || 'Not found',
        errorCode: 'NOT_FOUND',
        userMessage: detail || 'The requested resource was not found.',
      };
    }

    if (status === 429) {
      const retryAfterSeconds = parseRetryAfter(axiosError);
      return {
        status,
        message: detail || 'Rate limited',
        errorCode: 'RATE_LIMIT',
        userMessage: retryAfterSeconds
          ? `Too many requests. Try again in ${retryAfterSeconds} seconds.`
          : 'Too many requests. Please try again later.',
        retryAfterSeconds,
      };
    }

    if (status >= 500) {
      return {
        status,
        message: detail || 'Server error',
        errorCode: 'SERVER_ERROR',
        userMessage: 'Server error. Please try again later.',
      };
    }

    if (status === 0) {
      return {
        status: 0,
        message: 'Network error',
        errorCode: 'NETWORK_ERROR',
        userMessage: 'Network connection error. Please check your connection.',
      };
    }

    return {
      status: status || 0,
      message: axiosError.message,
      userMessage: detail || 'An error occurred. Please try again.',
      fieldErrors,
    };
  }

  if (error instanceof Error) {
    return {
      status: 0,
      message: error.message,
      userMessage: 'An unexpected error occurred.',
    };
  }

  return {
    status: 0,
    message: 'Unknown error',
    userMessage: 'An unexpected error occurred.',
  };
};
