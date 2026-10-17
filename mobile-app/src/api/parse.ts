import { ZodType } from 'zod';
import { NormalizedError } from '../utils/errorNormalizer';

export const parseApi = <T>(schema: ZodType<T>, data: unknown): T => {
  const result = schema.safeParse(data);
  if (!result.success) {
    const error: NormalizedError = {
      status: 0,
      message: result.error.message,
      errorCode: 'CONTRACT',
      userMessage: 'Unexpected server response. Please try again.',
    };
    throw error;
  }
  return result.data;
};
