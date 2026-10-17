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
import { EmptyState } from '../../components/EmptyState';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { MonthSelector } from '../../components/MonthSelector';
import { currentMonth } from '../../utils/dates';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import {
  useApproveUser,
  useAssignManager,
  useManagerAssignments,
  useMealSummary,
  usePendingUsers,
} from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

const assignSchema = z.object({
  user_id: z.string().regex(/^\d+$/, 'User id is required'),
  month: z.string().regex(/^\d{4}-\d{2}$/),
});

export const ManagerScreen: React.FC = () => {
  const { isSuperManager, isManager, refreshUserProfile } = useAuthStore();
  const [month, setMonth] = useState(currentMonth());
  const pendingUsers = usePendingUsers(isSuperManager());
  const assignments = useManagerAssignments(isSuperManager());
  const members = useMealSummary(month, isSuperManager());
  const approve = useApproveUser();
  const assign = useAssignManager();
  const { control, handleSubmit, setValue } = useForm({
    defaultValues: { user_id: '', month: currentMonth() },
  });

  const onAssign = handleSubmit(async (values) => {
    const parsed = assignSchema.safeParse(values);
    if (!parsed.success) {
      return;
    }
    await assign.mutateAsync({ user_id: Number(parsed.data.user_id), month: parsed.data.month });
    await refreshUserProfile();
  });

  if (!isManager()) {
    return <EmptyState title="Manager only" message="You do not have access to this screen." />;
  }

  const error = (pendingUsers.error || assignments.error || assign.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={pendingUsers.isRefetching || assignments.isRefetching}
          onRefresh={() => {
            pendingUsers.refetch();
            assignments.refetch();
            members.refetch();
          }}
        />
      }
    >
      <View style={styles.pad}>
        {error ? <ErrorBanner error={error} /> : null}

        {isSuperManager() ? (
          <>
            <Text style={styles.heading}>Pending members</Text>
            {pendingUsers.isLoading ? (
              <ScreenLoader />
            ) : !pendingUsers.data?.length ? (
              <EmptyState title="No pending users" />
            ) : (
              pendingUsers.data.map((user) => (
                <View key={user.id} style={styles.card}>
                  <Text style={styles.title}>{user.full_name}</Text>
                  <Text style={styles.meta}>{user.mobile_number}</Text>
                  <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Approve member"
 onPress={() => approve.mutate(user.id)}>
                    {approve.isPending ? (
                      <ActivityIndicator color="#fff" />
                    ) : (
                      <Text style={styles.buttonText}>Approve</Text>
                    )}
                  </TouchableOpacity>
                </View>
              ))
            )}

            <Text style={styles.heading}>Assign monthly manager</Text>
            <MonthSelector
              month={month}
              onChange={(value) => {
                setMonth(value);
                setValue('month', value);
              }}
            />
            <Text style={styles.meta}>Pick a member from this month&apos;s meal summary, or enter user id.</Text>
            {(members.data?.members ?? []).map((member) => (
              <TouchableOpacity
                key={member.user_id}
                style={styles.pick}
                onPress={() => setValue('user_id', String(member.user_id))}
              >
                <Text>
                  {member.full_name} (#{member.user_id})
                </Text>
              </TouchableOpacity>
            ))}
            <Controller
              control={control}
              name="user_id"
              render={({ field }) => (
                <FormField
                  label="User id"
                  value={field.value}
                  onChangeText={field.onChange}
                  keyboardType="numeric"
                />
              )}
            />
            <Controller
              control={control}
              name="month"
              render={({ field }) => (
                <FormField label="Month" value={field.value} onChangeText={field.onChange} />
              )}
            />
            <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Assign manager"
 onPress={onAssign} disabled={assign.isPending}>
              {assign.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Assign manager</Text>
              )}
            </TouchableOpacity>

            <Text style={styles.heading}>Active assignment</Text>
            {assignments.data?.active ? (
              <View style={styles.card}>
                <Text style={styles.title}>{assignments.data.active.full_name}</Text>
                <Text style={styles.meta}>
                  {assignments.data.active.month} · {assignments.data.active.mobile_number}
                </Text>
              </View>
            ) : (
              <EmptyState title="No active manager" />
            )}

            <Text style={styles.heading}>History</Text>
            {(assignments.data?.history ?? []).map((item) => (
              <View key={item.id} style={styles.card}>
                <Text style={styles.title}>{item.full_name}</Text>
                <Text style={styles.meta}>
                  {item.month} {item.is_active ? '(active)' : ''}
                </Text>
              </View>
            ))}
          </>
        ) : (
          <EmptyState
            title="Monthly manager"
            message="Use Meals, Deposits, Expenses, Bills, and Complaints tabs for your duties. User approval and manager assignment require Super Manager."
          />
        )}
      </View>
    </KeyboardScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  pad: { padding: 16, paddingBottom: 48 },
  heading: { fontSize: 16, fontWeight: '700', marginVertical: 12 },
  card: { borderWidth: 1, borderColor: theme.colors.border, borderRadius: 12, padding: 12, marginBottom: 8 },
  title: { fontWeight: '700' },
  meta: { color: theme.colors.text.secondary, marginTop: 4, marginBottom: 8 },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 12,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 8,
  },
  buttonText: { color: '#fff', fontWeight: '600' },
  pick: {
    padding: 10,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 8,
    marginBottom: 6,
  },
});
