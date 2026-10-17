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
import { EmptyState } from '../../components/EmptyState';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { currentMonth } from '../../utils/dates';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import { useBillActions, useMyBill } from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

const amountSchema = z.object({
  total: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Enter a valid amount'),
  paid: z.string().optional(),
});

export const BillsScreen: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const { isManager, isSuperManager } = useAuthStore();
  const bill = useMyBill(month);
  const actions = useBillActions(month);
  const rentForm = useForm({ defaultValues: { total: '', paid: '0' } });
  const elecForm = useForm({ defaultValues: { total: '', paid: '0' } });

  const submitRent = rentForm.handleSubmit(async (values) => {
    const parsed = amountSchema.safeParse(values);
    if (!parsed.success) return;
    await actions.setHouseRent.mutateAsync({ month, total: parsed.data.total, paid: parsed.data.paid || '0' });
    rentForm.reset();
  });

  const submitElec = elecForm.handleSubmit(async (values) => {
    const parsed = amountSchema.safeParse(values);
    if (!parsed.success) return;
    await actions.setElectricity.mutateAsync({ month, total: parsed.data.total, paid: parsed.data.paid || '0' });
    elecForm.reset();
  });

  const error = (bill.error ||
    actions.generate.error ||
    actions.setHouseRent.error ||
    actions.setElectricity.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={bill.isRefetching} onRefresh={() => bill.refetch()} />}
    >
      <View style={styles.pad}>
        <MonthSelector month={month} onChange={setMonth} />
        {error ? <ErrorBanner error={error} /> : null}

        {bill.isLoading ? (
          <ScreenLoader />
        ) : !bill.data?.bill ? (
          <EmptyState title="No bill yet" message={bill.data?.detail || 'Bills have not been generated for this month.'} />
        ) : (
          <View style={styles.card}>
            <Text style={styles.title}>Your bill</Text>
            <Text style={styles.line}>Seat: {bill.data.bill.seat_bill}</Text>
            <Text style={styles.line}>Current share: {bill.data.bill.current_bill_share}</Text>
            <Text style={styles.line}>House rent share: {bill.data.bill.house_rent_share}</Text>
            <Text style={styles.line}>Electricity share: {bill.data.bill.electricity_share}</Text>
            <Text style={styles.line}>Meal cost: {bill.data.bill.meal_cost}</Text>
            <Text style={styles.line}>Total due: {bill.data.bill.total_due}</Text>
            <Text style={styles.line}>Deposits: {bill.data.bill.total_deposit}</Text>
            <Text style={styles.balance}>Balance: {bill.data.bill.balance}</Text>
          </View>
        )}

        {bill.data?.cycle ? (
          <View style={styles.card}>
            <Text style={styles.title}>Cycle</Text>
            <Text style={styles.line}>Meal rate: {bill.data.cycle.meal_rate}</Text>
            <Text style={styles.line}>Meals: {bill.data.cycle.total_meal_count}</Text>
            <Text style={styles.line}>
              House rent: {bill.data.cycle.house_rent_total} (paid {bill.data.cycle.house_rent_paid})
            </Text>
            <Text style={styles.line}>
              Electricity: {bill.data.cycle.electricity_bill_total} (paid {bill.data.cycle.electricity_bill_paid})
            </Text>
          </View>
        ) : null}

        {isManager() ? (
          <TouchableOpacity
            style={styles.button}
            accessibilityRole="button"
 accessibilityLabel="Generate bills"
 onPress={() => actions.generate.mutate()}
            disabled={actions.generate.isPending}
          >
            {actions.generate.isPending ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Generate bills</Text>
            )}
          </TouchableOpacity>
        ) : null}

        {isSuperManager() ? (
          <>
            <Text style={styles.heading}>House rent</Text>
            <Controller
              control={rentForm.control}
              name="total"
              render={({ field }) => (
                <FormField label="Total" value={field.value} onChangeText={field.onChange} keyboardType="numeric" />
              )}
            />
            <Controller
              control={rentForm.control}
              name="paid"
              render={({ field }) => (
                <FormField label="Paid" value={field.value} onChangeText={field.onChange} keyboardType="numeric" />
              )}
            />
            <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Save house rent"
 onPress={submitRent}>
              <Text style={styles.buttonText}>Save house rent</Text>
            </TouchableOpacity>

            <Text style={styles.heading}>Electricity</Text>
            <Controller
              control={elecForm.control}
              name="total"
              render={({ field }) => (
                <FormField label="Total" value={field.value} onChangeText={field.onChange} keyboardType="numeric" />
              )}
            />
            <Controller
              control={elecForm.control}
              name="paid"
              render={({ field }) => (
                <FormField label="Paid" value={field.value} onChangeText={field.onChange} keyboardType="numeric" />
              )}
            />
            <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Save electricity"
 onPress={submitElec}>
              <Text style={styles.buttonText}>Save electricity</Text>
            </TouchableOpacity>
          </>
        ) : null}
      </View>
    </KeyboardScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  pad: { padding: 16, paddingBottom: 48 },
  card: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
  },
  title: { fontWeight: '700', marginBottom: 8 },
  line: { marginBottom: 4, color: theme.colors.text.secondary },
  balance: { marginTop: 8, fontWeight: '700', fontSize: 16 },
  heading: { fontSize: 16, fontWeight: '700', marginTop: 12, marginBottom: 8 },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  buttonText: { color: '#fff', fontWeight: '600' },
});
