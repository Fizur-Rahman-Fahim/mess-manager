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
import { MonthSelector } from '../../components/MonthSelector';
import { FormField } from '../../components/FormField';
import { StatusBadge } from '../../components/StatusBadge';
import { EmptyState } from '../../components/EmptyState';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { currentDate, currentMonth, formatDate } from '../../utils/dates';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import {
  useClaimDeposit,
  useDepositReview,
  useMyDeposits,
  usePendingDeposits,
} from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

const claimSchema = z.object({
  amount: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Enter a valid amount'),
  date_claimed: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Use YYYY-MM-DD'),
  note: z.string().optional(),
});

export const DepositsScreen: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const [tab, setTab] = useState<'mine' | 'pending'>('mine');
  const { isManager } = useAuthStore();
  const mine = useMyDeposits(month);
  const pendingActive = isManager() && tab === 'pending';
  const pending = usePendingDeposits(pendingActive);
  const claim = useClaimDeposit(month);
  const review = useDepositReview();
  const { control, handleSubmit, reset, setError } = useForm({
    defaultValues: { amount: '', date_claimed: currentDate(), note: '' },
  });

  const onClaim = handleSubmit(async (values) => {
    const parsed = claimSchema.safeParse(values);
    if (!parsed.success) {
      parsed.error.issues.forEach((issue) => {
        setError(String(issue.path[0]) as 'amount' | 'date_claimed' | 'note', { message: issue.message });
      });
      return;
    }
    await claim.mutateAsync(parsed.data);
    reset({ amount: '', date_claimed: currentDate(), note: '' });
  });

  const error = (mine.error || (pendingActive ? pending.error : null) || claim.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl
          refreshing={mine.isRefetching || pending.isRefetching}
          onRefresh={() => {
            mine.refetch();
            if (pendingActive) pending.refetch();
          }}
        />
      }
    >
      <View style={styles.pad}>
        <MonthSelector month={month} onChange={setMonth} />
        {isManager() ? (
          <View style={styles.tabs}>
            {(['mine', 'pending'] as const).map((key) => (
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
            <Text style={styles.heading}>New claim</Text>
            <Controller
              control={control}
              name="amount"
              render={({ field, fieldState }) => (
                <FormField
                  label="Amount"
                  value={field.value}
                  onChangeText={field.onChange}
                  keyboardType="numeric"
                  error={fieldState.error?.message}
                />
              )}
            />
            <Controller
              control={control}
              name="date_claimed"
              render={({ field, fieldState }) => (
                <FormField
                  label="Date claimed"
                  value={field.value}
                  onChangeText={field.onChange}
                  placeholder="YYYY-MM-DD"
                  error={fieldState.error?.message}
                />
              )}
            />
            <Controller
              control={control}
              name="note"
              render={({ field }) => (
                <FormField label="Note" value={field.value} onChangeText={field.onChange} />
              )}
            />
            <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Submit deposit claim"
 onPress={onClaim} disabled={claim.isPending}>
              {claim.isPending ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.buttonText}>Submit claim</Text>
              )}
            </TouchableOpacity>

            <Text style={styles.heading}>History</Text>
            {mine.isLoading ? (
              <ScreenLoader />
            ) : !mine.data?.deposits.length ? (
              <EmptyState title="No deposits" message="No claims for this month." />
            ) : (
              mine.data.deposits.map((item) => (
                <View key={item.id} style={styles.card}>
                  <View style={styles.rowBetween}>
                    <Text style={styles.amount}>{item.amount}</Text>
                    <StatusBadge status={item.status} label={item.status_display} />
                  </View>
                  <Text style={styles.meta}>{formatDate(item.date_claimed)}</Text>
                  {item.note ? <Text style={styles.meta}>{item.note}</Text> : null}
                </View>
              ))
            )}
          </>
        ) : (
          <>
            <Text style={styles.heading}>Pending review</Text>
            {pending.isLoading ? (
              <ScreenLoader />
            ) : !pending.data?.deposits.length ? (
              <EmptyState title="None pending" />
            ) : (
              pending.data.deposits.map((item) => (
                <View key={item.id} style={styles.card}>
                  <Text style={styles.amount}>
                    {item.user_name} · {item.amount}
                  </Text>
                  <Text style={styles.meta}>
                    {item.user_mobile} · {formatDate(item.date_claimed)}
                  </Text>
                  <View style={styles.actions}>
                    <TouchableOpacity
                      style={styles.approve}
                      accessibilityRole="button"
 accessibilityLabel="Approve deposit"
 onPress={() => review.approve.mutate(item.id)}
                    >
                      <Text style={styles.actionText}>Approve</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={styles.reject}
                      accessibilityRole="button"
 accessibilityLabel="Reject deposit"
 onPress={() => review.reject.mutate(item.id)}
                    >
                      <Text style={styles.actionText}>Reject</Text>
                    </TouchableOpacity>
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
  pad: { padding: theme.spacing.md, paddingBottom: 48 },
  tabs: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: theme.radius.full,
    backgroundColor: theme.colors.surfaceVariant,
  },
  tabActive: { backgroundColor: theme.colors.primary },
  tabText: { textTransform: 'capitalize' },
  tabTextActive: { color: '#fff', fontWeight: '600' },
  heading: { fontSize: 16, fontWeight: '700', marginVertical: 12 },
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
  amount: { fontWeight: '700', fontSize: 16 },
  meta: { color: theme.colors.text.secondary, marginTop: 4 },
  actions: { flexDirection: 'row', gap: 8, marginTop: 10 },
  approve: { backgroundColor: theme.colors.badge.approved, padding: 8, borderRadius: 8, flex: 1, alignItems: 'center' },
  reject: { backgroundColor: theme.colors.badge.rejected, padding: 8, borderRadius: 8, flex: 1, alignItems: 'center' },
  actionText: { color: '#fff', fontWeight: '600' },
});
