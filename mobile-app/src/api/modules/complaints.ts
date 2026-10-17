import { apiClient } from '../client';
import { parseApi } from '../parse';
import { complaintSchema } from '../schemas';

export const getMyComplaints = async () => {
  const data = await apiClient.get<unknown>('/complaints/my-complaints/');
  return parseApi(complaintSchema.array(), data);
};

export const createComplaint = async (payload: { title: string; description: string }) => {
  const data = await apiClient.post<unknown>('/complaints/', payload);
  return parseApi(complaintSchema, data);
};

export const getAllComplaints = async () => {
  const data = await apiClient.get<unknown>('/complaints/all/');
  return parseApi(complaintSchema.array(), data);
};

export const updateComplaintStatus = async (
  complaintId: number,
  status: 'pending' | 'in_progress' | 'resolved',
) => {
  const data = await apiClient.patch<unknown>(`/complaints/${complaintId}/status/`, { status });
  return parseApi(complaintSchema, data);
};
