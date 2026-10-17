import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useAuthStore } from '../../stores/authStore';
import { theme } from '../../theme/colors';
import { currentMonth } from '../../utils/dates';
import { useMyBill, useMyMeals } from '../../hooks/queries';

export const DashboardScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const { user, isManager, logout } = useAuthStore();
  const month = currentMonth();
  const mealsQuery = useMyMeals(month);
  const billQuery = useMyBill(month);

  const mealCount = mealsQuery.data?.meals.reduce((sum, meal) => {
    return sum + Number(meal.breakfast) + Number(meal.lunch) + Number(meal.dinner);
  }, 0);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome, {user?.full_name || 'Member'}</Text>
          <Text style={styles.subtitle}>
            {user?.mobile_number} · {user?.role}
          </Text>
        </View>

        <View style={styles.statusCard}>
          <Text style={styles.statusTitle}>{month}</Text>
          <Text style={styles.statusLine}>
            Meals logged (on): {mealsQuery.isLoading ? '…' : mealCount ?? '—'}
          </Text>
          <Text style={styles.statusLine}>
            Balance:{' '}
            {billQuery.data?.bill ? billQuery.data.bill.balance : billQuery.data?.detail || 'No bill yet'}
          </Text>
        </View>

        <Text style={styles.sectionTitle}>Quick access</Text>
        <View style={styles.cardGrid}>
          {[
            { key: 'Meals', title: 'Meals', desc: 'Log meals' },
            { key: 'Deposits', title: 'Deposits', desc: 'Claims' },
            { key: 'Bills', title: 'Bills', desc: 'Your bill' },
            { key: 'Complaints', title: 'Complaints', desc: 'Raise issues' },
          ].map((item) => (
            <TouchableOpacity
              key={item.key}
              style={styles.card}
              onPress={() => navigation.navigate(item.key)}
              accessibilityRole="button"
              accessibilityLabel={`${item.title}: ${item.desc}`}
            >
              <Text style={styles.cardTitle}>{item.title}</Text>
              <Text style={styles.cardDesc}>{item.desc}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {isManager() ? (
          <>
            <Text style={styles.sectionTitle}>Manager</Text>
            <View style={styles.cardGrid}>
              <TouchableOpacity
                style={styles.card}
                onPress={() => navigation.navigate('Expenses')}
                accessibilityRole="button"
                accessibilityLabel="Expenses: Bazar"
              >
                <Text style={styles.cardTitle}>Expenses</Text>
                <Text style={styles.cardDesc}>Bazar</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.card}
                onPress={() => navigation.navigate('Manager')}
                accessibilityRole="button"
                accessibilityLabel="Operations"
              >
                <Text style={styles.cardTitle}>Operations</Text>
                <Text style={styles.cardDesc}>Approvals</Text>
              </TouchableOpacity>
            </View>
          </>
        ) : null}

        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  content: { paddingHorizontal: theme.spacing.lg, paddingVertical: theme.spacing.md },
  header: { marginBottom: theme.spacing.lg },
  greeting: { fontSize: 24, fontWeight: '700', color: theme.colors.text.primary, marginBottom: 4 },
  subtitle: { fontSize: 14, color: theme.colors.text.secondary },
  statusCard: {
    backgroundColor: theme.colors.primaryContainer,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.xl,
  },
  statusTitle: { fontWeight: '700', marginBottom: theme.spacing.sm, color: theme.colors.onPrimaryContainer },
  statusLine: { color: theme.colors.onPrimaryContainer, marginBottom: 4 },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.md,
  },
  cardGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.md, marginBottom: theme.spacing.xl },
  card: {
    width: '47%',
    padding: theme.spacing.md,
    borderRadius: theme.radius.md,
    backgroundColor: theme.colors.surfaceVariant,
    ...theme.shadows.elevation2,
  },
  cardTitle: { fontSize: 14, fontWeight: '600', color: theme.colors.text.primary, marginBottom: 4 },
  cardDesc: { fontSize: 12, color: theme.colors.text.tertiary },
  logoutButton: {
    paddingVertical: theme.spacing.md,
    borderRadius: theme.radius.md,
    borderWidth: 2,
    borderColor: theme.colors.error,
    marginBottom: theme.spacing.xl,
  },
  logoutButtonText: { color: theme.colors.error, fontSize: 16, fontWeight: '600', textAlign: 'center' },
});
