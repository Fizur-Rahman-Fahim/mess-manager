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
import * as ImagePicker from 'expo-image-picker';
import * as ImageManipulator from 'expo-image-manipulator';
import { MonthSelector } from '../../components/MonthSelector';
import { FormField } from '../../components/FormField';
import { EmptyState } from '../../components/EmptyState';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { currentDate, currentMonth, formatDate } from '../../utils/dates';
import { theme } from '../../theme/colors';
import { useAddBazarExpense, useBazarExpenses } from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

const schema = z.object({
  bazar_type: z.enum(['boro', 'choto']),
  amount: z.string().regex(/^\d+(\.\d{1,2})?$/, 'Enter a valid amount'),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Use YYYY-MM-DD'),
  description: z.string().optional(),
});

export const ExpensesScreen: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const [receiptUri, setReceiptUri] = useState<string | null>(null);
  const query = useBazarExpenses(month, true);
  const add = useAddBazarExpense(month);
  const { control, handleSubmit, reset, setError, watch } = useForm({
    defaultValues: { bazar_type: 'boro' as 'boro' | 'choto', amount: '', date: currentDate(), description: '' },
  });
  const bazarType = watch('bazar_type');

  const pickReceipt = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 1,
    });
    if (result.canceled || !result.assets[0]) {
      return;
    }
    const compressed = await ImageManipulator.manipulateAsync(
      result.assets[0].uri,
      [{ resize: { width: 1280 } }],
      { compress: 0.7, format: ImageManipulator.SaveFormat.JPEG },
    );
    setReceiptUri(compressed.uri);
  };

  const onSubmit = handleSubmit(async (values) => {
    const parsed = schema.safeParse(values);
    if (!parsed.success) {
      parsed.error.issues.forEach((issue) => {
        setError(String(issue.path[0]) as 'amount' | 'date' | 'description' | 'bazar_type', {
          message: issue.message,
        });
      });
      return;
    }
    const formData = new FormData();
    formData.append('bazar_type', parsed.data.bazar_type);
    formData.append('amount', parsed.data.amount);
    formData.append('date', parsed.data.date);
    formData.append('description', parsed.data.description || '');
    if (receiptUri) {
      formData.append('receipt_image', {
        uri: receiptUri,
        name: 'receipt.jpg',
        type: 'image/jpeg',
      } as unknown as Blob);
    }
    await add.mutateAsync(formData);
    reset({ bazar_type: 'boro', amount: '', date: currentDate(), description: '' });
    setReceiptUri(null);
  });

  const error = (query.error || add.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={query.isRefetching} onRefresh={() => query.refetch()} />}
    >
      <View style={styles.pad}>
        <MonthSelector month={month} onChange={setMonth} />
        {error ? <ErrorBanner error={error} /> : null}

        {query.isLoading ? (
          <ScreenLoader />
        ) : query.data ? (
          <View style={styles.summary}>
            <Text style={styles.summaryLine}>Boro: {query.data.boro_total}</Text>
            <Text style={styles.summaryLine}>Choto: {query.data.choto_total}</Text>
            <Text style={styles.summaryLine}>Total: {query.data.total_bazar}</Text>
            <Text style={styles.summaryLine}>Meal rate: {query.data.meal_rate}</Text>
          </View>
        ) : null}

        <Text style={styles.heading}>Add expense</Text>
        <View style={styles.tabs}>
          {(['boro', 'choto'] as const).map((type) => (
            <Controller
              key={type}
              control={control}
              name="bazar_type"
              render={({ field }) => (
                <TouchableOpacity
                  style={[styles.tab, field.value === type && styles.tabActive]}
                  onPress={() => field.onChange(type)}
 accessibilityRole="tab"
 accessibilityState={{ selected: field.value === type }}
                >
                  <Text style={[styles.tabText, field.value === type && styles.tabTextActive]}>
                    {type === 'boro' ? 'Boro bazar' : 'Choto bazar'}
                  </Text>
                </TouchableOpacity>
              )}
            />
          ))}
        </View>
        <Text style={styles.hint}>Selected: {bazarType}</Text>
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
          name="date"
          render={({ field, fieldState }) => (
            <FormField
              label="Date"
              value={field.value}
              onChangeText={field.onChange}
              placeholder="YYYY-MM-DD"
              error={fieldState.error?.message}
            />
          )}
        />
        <Controller
          control={control}
          name="description"
          render={({ field }) => (
            <FormField label="Description" value={field.value} onChangeText={field.onChange} />
          )}
        />
        <TouchableOpacity style={styles.secondary} accessibilityRole="button"
 accessibilityLabel="Attach receipt photo"
 onPress={pickReceipt}>
          <Text style={styles.secondaryText}>{receiptUri ? 'Receipt selected' : 'Attach receipt (optional)'}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Save expense"
 onPress={onSubmit} disabled={add.isPending}>
          {add.isPending ? <ActivityIndicator color="#fff" /> : <Text style={styles.buttonText}>Save expense</Text>}
        </TouchableOpacity>

        <Text style={styles.heading}>This month</Text>
        {!query.data?.expenses.length ? (
          <EmptyState title="No expenses" />
        ) : (
          query.data.expenses.map((item) => (
            <View key={item.id} style={styles.card}>
              <Text style={styles.amount}>
                {item.bazar_type_display} · {item.amount}
              </Text>
              <Text style={styles.meta}>
                {formatDate(item.date)} · {item.added_by_name}
              </Text>
              {item.description ? <Text style={styles.meta}>{item.description}</Text> : null}
            </View>
          ))
        )}
      </View>
    </KeyboardScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  pad: { padding: 16, paddingBottom: 48 },
  summary: {
    backgroundColor: theme.colors.primaryContainer,
    padding: 12,
    borderRadius: 12,
    marginBottom: 16,
  },
  summaryLine: { color: theme.colors.onPrimaryContainer, marginBottom: 2 },
  heading: { fontSize: 16, fontWeight: '700', marginVertical: 8 },
  tabs: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  tab: {
    flex: 1,
    padding: 10,
    borderRadius: 10,
    backgroundColor: theme.colors.surfaceVariant,
    alignItems: 'center',
  },
  tabActive: { backgroundColor: theme.colors.primary },
  tabText: { fontWeight: '600' },
  tabTextActive: { color: '#fff' },
  hint: { marginBottom: 8, color: theme.colors.text.secondary, fontSize: 12 },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
  },
  buttonText: { color: '#fff', fontWeight: '600' },
  secondary: { padding: 12, alignItems: 'center', marginBottom: 12 },
  secondaryText: { color: theme.colors.primary, fontWeight: '600' },
  card: { borderWidth: 1, borderColor: theme.colors.border, borderRadius: 12, padding: 12, marginBottom: 8 },
  amount: { fontWeight: '700' },
  meta: { color: theme.colors.text.secondary, marginTop: 4 },
});
