import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Controller, useForm } from 'react-hook-form';
import { z } from 'zod';
import { FormField } from '../../components/FormField';
import { StatusBadge } from '../../components/StatusBadge';
import { EmptyState } from '../../components/EmptyState';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import {
  useAllComplaints,
  useCreateComplaint,
  useMyComplaints,
  useUpdateComplaintStatus,
} from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

const schema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
});

export const ComplaintsScreen: React.FC = () => {
  const [tab, setTab] = useState<'mine' | 'all'>('mine');
  const { isManager } = useAuthStore();
  const mine = useMyComplaints();
  const allActive = isManager() && tab === 'all';
  const all = useAllComplaints(allActive);
  const create = useCreateComplaint();
  const updateStatus = useUpdateComplaintStatus();
  const { control, handleSubmit, reset, setError } = useForm({
    defaultValues: { title: '', description: '' },
  });

  const onCreate = handleSubmit(async (values) => {
    const parsed = schema.safeParse(values);
    if (!parsed.success) {
      parsed.error.issues.forEach((issue) => {
        setError(String(issue.path[0]) as 'title' | 'description', { message: issue.message });
      });
      return;
    }
    await create.mutateAsync(parsed.data);
    reset();
  });

  const error = (mine.error || (allActive ? all.error : null) || create.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={mine.isRefetching || all.isRefetching}
          onRefresh={() => {
            mine.refetch();
            if (allActive) all.refetch();
          }}
        />
      }
    >
      <View style={styles.pad}>
        {isManager() ? (
          <View style={styles.tabs}>
            {(['mine', 'all'] as const).map((key) => (
              <TouchableOpacity
                key={key}
                style={[styles.tab, tab === key && styles.tabActive]}
                onPress={() => setTab(key)}
 accessibilityRole="tab"
 accessibilityState={{ selected: tab === key }}
              >
                <Text style={[styles.tabText, tab === key && styles.tabTextActive]}>{key}</Text>
              </TouchableOpacity>
            ))}
          </View>
        ) : null}

        {error ? <ErrorBanner error={error} /> : null}

        {tab === 'mine' || !isManager() ? (
          <>
            <Text style={styles.heading}>New complaint</Text>
            <Controller
              control={control}
              name="title"
              render={({ field, fieldState }) => (
                <FormField
                  label="Title"
                  value={field.value}
                  onChangeText={field.onChange}
                  error={fieldState.error?.message}
                />
              )}
            />
            <Controller
              control={control}
              name="description"
              render={({ field, fieldState }) => (
                <FormField
                  label="Description"
                  value={field.value}
                  onChangeText={field.onChange}
                  multiline
                  error={fieldState.error?.message}
                />
              )}
            />
            <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Submit complaint"
 onPress={onCreate} disabled={create.isPending}>
              {create.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Submit</Text>
              )}
            </TouchableOpacity>
            {mine.isLoading ? (
              <ScreenLoader />
            ) : !mine.data?.length ? (
              <EmptyState title="No complaints" />
            ) : (
              mine.data.map((item) => (
                <View key={item.id} style={styles.card}>
                  <View style={styles.rowBetween}>
                    <Text style={styles.title}>{item.title}</Text>
                    <StatusBadge status={item.status} />
                  </View>
                  <Text style={styles.meta}>{item.description}</Text>
                </View>
              ))
            )}
          </>
        ) : (
          <>
            {all.isLoading ? (
              <ScreenLoader />
            ) : !all.data?.length ? (
              <EmptyState title="No complaints" />
            ) : (
              all.data.map((item) => (
                <View key={item.id} style={styles.card}>
                  <Text style={styles.title}>{item.title}</Text>
                  <Text style={styles.meta}>
                    {item.raised_by_name} · {item.status}
                  </Text>
                  <View style={styles.actions}>
                    {(['pending', 'in_progress', 'resolved'] as const).map((status) => (
                      <TouchableOpacity
                        key={status}
                        style={styles.statusBtn}
                        onPress={() => updateStatus.mutate({ id: item.id, status })}
 accessibilityRole="button"
 accessibilityLabel={`Mark complaint as ${status}`}
                      >
                        <Text style={styles.statusBtnText}>{status.replace('_', ' ')}</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              ))
            )}
          </>
        )}
      </View>
    </KeyboardScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  pad: { padding: 16, paddingBottom: 48 },
  tabs: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: theme.colors.surfaceVariant,
  },
  tabActive: { backgroundColor: theme.colors.primary },
  tabText: { textTransform: 'capitalize' },
  tabTextActive: { color: '#fff', fontWeight: '600' },
  heading: { fontSize: 16, fontWeight: '700', marginBottom: 8 },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: { color: '#fff', fontWeight: '600' },
  card: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 12,
    padding: 12,
    marginBottom: 10,
  },
  rowBetween: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontWeight: '700', flex: 1, marginRight: 8 },
  meta: { color: theme.colors.text.secondary, marginTop: 6 },
  actions: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 10 },
  statusBtn: {
    backgroundColor: theme.colors.secondaryContainer,
    paddingHorizontal: 8,
    paddingVertical: 6,
    borderRadius: 8,
  },
  statusBtnText: { fontSize: 12, fontWeight: '600' },
});
