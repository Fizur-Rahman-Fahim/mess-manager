import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { Controller, useForm } from 'react-hook-form';
import { FormField } from '../../components/FormField';
import { ScreenLoader } from '../../components/ScreenLoader';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import { usePatchSettings, useSettings } from '../../hooks/queries';
import { NormalizedError } from '../../utils/errorNormalizer';

export const SettingsScreen: React.FC = () => {
  const { user, isSuperManager, logout } = useAuthStore();
  const settings = useSettings();
  const patch = usePatchSettings();
  const { control, handleSubmit, reset } = useForm({
    defaultValues: {
      seat_bill_default: '',
      current_bill_default: '',
      breakfast_meal_value: '',
      lunch_meal_value: '',
      dinner_meal_value: '',
      meal_off_cutoff_time: '',
    },
  });

  useEffect(() => {
    if (settings.data) {
      reset({
        seat_bill_default: settings.data.seat_bill_default,
        current_bill_default: settings.data.current_bill_default,
        breakfast_meal_value: settings.data.breakfast_meal_value,
        lunch_meal_value: settings.data.lunch_meal_value,
        dinner_meal_value: settings.data.dinner_meal_value,
        meal_off_cutoff_time: String(settings.data.meal_off_cutoff_time).slice(0, 8),
      });
    }
  }, [settings.data, reset]);

  const onSave = handleSubmit(async (values) => {
    await patch.mutateAsync(values);
  });

  const error = (settings.error || patch.error) as unknown as NormalizedError | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={settings.isRefetching} onRefresh={() => settings.refetch()} />}
    >
      <View style={styles.pad}>
        <View style={styles.card}>
          <Text style={styles.title}>{user?.full_name}</Text>
          <Text style={styles.meta}>{user?.mobile_number}</Text>
          <Text style={styles.meta}>{user?.role}</Text>
        </View>

        {error ? <ErrorBanner error={error} /> : null}
        {settings.isLoading ? <ScreenLoader /> : null}

        <Text style={styles.heading}>Mess settings</Text>
        {(
          [
            ['seat_bill_default', 'Seat bill default'],
            ['current_bill_default', 'Current bill default'],
            ['breakfast_meal_value', 'Breakfast value'],
            ['lunch_meal_value', 'Lunch value'],
            ['dinner_meal_value', 'Dinner value'],
            ['meal_off_cutoff_time', 'Meal-off cutoff (HH:MM:SS)'],
          ] as const
        ).map(([name, label]) => (
          <Controller
            key={name}
            control={control}
            name={name}
            render={({ field }) => (
              <FormField
                label={label}
                value={field.value}
                onChangeText={field.onChange}
                keyboardType={name === 'meal_off_cutoff_time' ? 'default' : 'numeric'}
              />
            )}
          />
        ))}

        {isSuperManager() ? (
          <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Save settings"
 onPress={onSave} disabled={patch.isPending}>
            {patch.isPending ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Save settings</Text>
            )}
          </TouchableOpacity>
        ) : (
          <Text style={styles.meta}>Only a Super Manager can change these values.</Text>
        )}

        <TouchableOpacity style={styles.logout} accessibilityRole="button"
 accessibilityLabel="Log out"
 onPress={logout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
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
    marginBottom: 16,
  },
  title: { fontSize: 18, fontWeight: '700' },
  meta: { color: theme.colors.text.secondary, marginTop: 4 },
  heading: { fontSize: 16, fontWeight: '700', marginBottom: 8 },
  button: {
    backgroundColor: theme.colors.primary,
    padding: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  buttonText: { color: '#fff', fontWeight: '600' },
  logout: {
    marginTop: 24,
    padding: 14,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: theme.colors.error,
  },
  logoutText: { color: theme.colors.error, textAlign: 'center', fontWeight: '600' },
});
