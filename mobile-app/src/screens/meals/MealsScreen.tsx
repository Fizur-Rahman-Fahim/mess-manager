import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Switch,
  TextInput,
} from 'react-native';
import { MonthSelector } from '../../components/MonthSelector';
import { ScreenLoader } from '../../components/ScreenLoader';
import { EmptyState } from '../../components/EmptyState';
import { currentMonth, formatDate } from '../../utils/dates';
import { theme } from '../../theme/colors';
import { useAuthStore } from '../../stores/authStore';
import {
  useDailyMealSummary,
  useFixedMeals,
  useMealSummary,
  useMyMeals,
  useSetFixedMeals,
  useToggleMeal,
} from '../../hooks/queries';
import { ErrorBanner } from '../../components/ErrorBanner';
import { KeyboardScrollView } from '../../components/KeyboardScrollView';
import { NormalizedError } from '../../utils/errorNormalizer';

export const MealsScreen: React.FC = () => {
  const [month, setMonth] = useState(currentMonth());
  const [tab, setTab] = useState<'mine' | 'summary' | 'daily'>('mine');
  const { isManager } = useAuthStore();
  const myMeals = useMyMeals(month);
  const toggle = useToggleMeal(month);
  const summary = useMealSummary(month, isManager() && tab === 'summary');
  const daily = useDailyMealSummary(month, isManager() && tab === 'daily');
  const fixed = useFixedMeals(month, isManager());
  const setFixed = useSetFixedMeals(month);
  const [fixedCount, setFixedCount] = useState('');

  const refreshing = myMeals.isRefetching || summary.isRefetching || daily.isRefetching;
  const onRefresh = () => {
    myMeals.refetch();
    if (isManager()) {
      summary.refetch();
      daily.refetch();
      fixed.refetch();
    }
  };

  const error = (myMeals.error || summary.error || daily.error || toggle.error) as unknown as
    | NormalizedError
    | undefined;

  return (
    <KeyboardScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
    >
      <View style={styles.pad}>
        <MonthSelector month={month} onChange={setMonth} />
        {isManager() ? (
          <View style={styles.tabs}>
            {(['mine', 'summary', 'daily'] as const).map((key) => (
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

        {error ? <ErrorBanner error={error} onDismiss={() => toggle.reset()} /> : null}

        {isManager() && fixed.data ? (
          <View style={styles.fixedBox}>
            <Text style={styles.fixedLabel}>Fixed meals: {fixed.data.fixed_meal_count}</Text>
            <View style={styles.fixedRow}>
              <TextInput
                style={styles.fixedInput}
                value={fixedCount}
                onChangeText={setFixedCount}
                keyboardType="numeric"
                placeholder="New count"
                accessibilityLabel="Fixed meal count"
              />
              <TouchableOpacity
                style={styles.smallButton}
                accessibilityRole="button"
                accessibilityLabel="Save fixed meal count"
                onPress={() => {
                  const value = Number(fixedCount);
                  if (!Number.isNaN(value)) {
                    setFixed.mutate(value);
                  }
                }}
              >
                <Text style={styles.smallButtonText}>Update</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : null}

        {tab === 'mine' || !isManager() ? (
          myMeals.isLoading ? (
            <ScreenLoader />
          ) : !myMeals.data?.meals.length ? (
            <EmptyState title="No meals" message="No meal rows for this month." />
          ) : (
            myMeals.data.meals.map((meal) => (
              <View key={meal.date} style={styles.dayRow}>
                <Text style={styles.dayLabel}>{formatDate(meal.date)}</Text>
                {(['breakfast', 'lunch', 'dinner'] as const).map((slot) => (
                  <View key={slot} style={styles.switchCol}>
                    <Text style={styles.slot}>{slot[0].toUpperCase()}</Text>
                    <Switch
                      accessibilityLabel={`${slot} meal on ${formatDate(meal.date)}`}
                      value={meal[slot]}
                      disabled={!meal.can_edit || toggle.isPending}
                      onValueChange={(value) =>
                        toggle.mutate({
                          date: meal.date,
                          breakfast: slot === 'breakfast' ? value : meal.breakfast,
                          lunch: slot === 'lunch' ? value : meal.lunch,
                          dinner: slot === 'dinner' ? value : meal.dinner,
                        })
                      }
                    />
                  </View>
                ))}
              </View>
            ))
          )
        ) : null}

        {tab === 'summary' && isManager() ? (
          summary.isLoading ? (
            <ScreenLoader />
          ) : (
            (summary.data?.members ?? []).map((member) => (
              <View key={member.user_id} style={styles.card}>
                <Text style={styles.cardTitle}>{member.full_name}</Text>
                <Text style={styles.cardMeta}>
                  B {member.breakfast_count} · L {member.lunch_count} · D {member.dinner_count} · total{' '}
                  {member.total_meal_value}
                </Text>
              </View>
            ))
          )
        ) : null}

        {tab === 'daily' && isManager() ? (
          daily.isLoading ? (
            <ScreenLoader />
          ) : (
            (daily.data?.days ?? []).map((day) => (
              <View key={String(day.date)} style={styles.card}>
                <Text style={styles.cardTitle}>{formatDate(String(day.date))}</Text>
                <Text style={styles.cardMeta}>
                  B {day.breakfast_on}/{day.breakfast_off} · L {day.lunch_on}/{day.lunch_off} · D{' '}
                  {day.dinner_on}/{day.dinner_off}
                </Text>
              </View>
            ))
          )
        ) : null}
      </View>
    </KeyboardScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  pad: { padding: theme.spacing.md, paddingBottom: theme.spacing.xxl },
  tabs: { flexDirection: 'row', gap: 8, marginBottom: theme.spacing.md },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: theme.radius.full,
    backgroundColor: theme.colors.surfaceVariant,
  },
  tabActive: { backgroundColor: theme.colors.primary },
  tabText: { color: theme.colors.text.primary, textTransform: 'capitalize' },
  tabTextActive: { color: theme.colors.onPrimary, fontWeight: '600' },
  dayRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  dayLabel: { flex: 1, color: theme.colors.text.primary, fontSize: 13 },
  switchCol: { alignItems: 'center', marginLeft: 6 },
  slot: { fontSize: 10, color: theme.colors.text.tertiary },
  card: {
    padding: theme.spacing.md,
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.surface,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
  },
  cardTitle: { fontWeight: '600', color: theme.colors.text.primary },
  cardMeta: { color: theme.colors.text.secondary, marginTop: 4, fontSize: 13 },
  fixedBox: { marginBottom: theme.spacing.md },
  fixedLabel: { fontWeight: '600', marginBottom: 8 },
  fixedRow: { flexDirection: 'row', gap: 8, alignItems: 'center' },
  fixedInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.sm,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  smallButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: theme.radius.sm,
  },
  smallButtonText: { color: '#fff', fontWeight: '600' },
});
