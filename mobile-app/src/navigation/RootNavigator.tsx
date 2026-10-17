import React, { useEffect } from 'react';
import { ActivityIndicator, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuthStore } from '../stores/authStore';
import { theme } from '../theme/colors';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { RegisterScreen } from '../screens/auth/RegisterScreen';
import { PendingApprovalScreen } from '../screens/dashboard/PendingApprovalScreen';
import { DashboardScreen } from '../screens/dashboard/DashboardScreen';
import { MealsScreen } from '../screens/meals/MealsScreen';
import { DepositsScreen } from '../screens/deposits/DepositsScreen';
import { BillsScreen } from '../screens/bills/BillsScreen';
import { ComplaintsScreen } from '../screens/complaints/ComplaintsScreen';
import { ExpensesScreen } from '../screens/expenses/ExpensesScreen';
import { ManagerScreen } from '../screens/manager/ManagerScreen';
import { SettingsScreen } from '../screens/settings/SettingsScreen';
import { ErrorBanner } from '../components/ErrorBanner';

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

export type TabParamList = {
  Dashboard: undefined;
  Meals: undefined;
  Deposits: undefined;
  Bills: undefined;
  Settings: undefined;
};

export type AppStackParamList = {
  Tabs: undefined;
  Complaints: undefined;
  Expenses: undefined;
  Manager: undefined;
};

const AuthStack = createStackNavigator<AuthStackParamList>();
const AppStack = createStackNavigator<AppStackParamList>();
const Tab = createBottomTabNavigator<TabParamList>();

const headerOptions = {
  headerStyle: { backgroundColor: theme.colors.primary },
  headerTintColor: '#fff',
  headerTitleStyle: { fontWeight: '600' as const },
};

const AuthNavigator: React.FC = () => (
  <AuthStack.Navigator screenOptions={{ headerShown: false }}>
    <AuthStack.Screen name="Login">
      {({ navigation }) => <LoginScreen onNavigateToRegister={() => navigation.navigate('Register')} />}
    </AuthStack.Screen>
    <AuthStack.Screen name="Register">
      {({ navigation }) => <RegisterScreen onNavigateToLogin={() => navigation.navigate('Login')} />}
    </AuthStack.Screen>
  </AuthStack.Navigator>
);

const TabsNavigator: React.FC = () => (
  <Tab.Navigator
    screenOptions={{
      ...headerOptions,
      tabBarStyle: {
        backgroundColor: theme.colors.surface,
        borderTopColor: theme.colors.border,
        borderTopWidth: 1,
      },
      tabBarActiveTintColor: theme.colors.primary,
      tabBarInactiveTintColor: theme.colors.text.tertiary,
      tabBarIconStyle: { display: 'none' },
      tabBarHideOnKeyboard: true,
      tabBarLabelStyle: { fontSize: 13, fontWeight: '600', paddingBottom: 6 },
    }}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} options={{ title: 'Dashboard', tabBarLabel: 'Home' }} />
    <Tab.Screen name="Meals" component={MealsScreen} />
    <Tab.Screen name="Deposits" component={DepositsScreen} />
    <Tab.Screen name="Bills" component={BillsScreen} />
    <Tab.Screen name="Settings" component={SettingsScreen} />
  </Tab.Navigator>
);

const AppNavigator: React.FC = () => {
  // Subscribing to the store keeps role-based screens in sync (e.g. after manager assignment).
  const isManager = useAuthStore((state) =>
    Boolean(state.user?.is_monthly_manager || state.user?.is_super_manager),
  );

  return (
    <AppStack.Navigator screenOptions={headerOptions}>
      <AppStack.Screen name="Tabs" component={TabsNavigator} options={{ headerShown: false }} />
      <AppStack.Screen name="Complaints" component={ComplaintsScreen} />
      {isManager ? (
        <>
          <AppStack.Screen name="Expenses" component={ExpensesScreen} />
          <AppStack.Screen name="Manager" component={ManagerScreen} options={{ title: 'Operations' }} />
        </>
      ) : null}
    </AppStack.Navigator>
  );
};

const Centered: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <View style={styles.centered}>{children}</View>
);

export const RootNavigator: React.FC = () => {
  const isBootstrapping = useAuthStore((s) => s.isBootstrapping);
  const bootstrapError = useAuthStore((s) => s.bootstrapError);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const showPendingApproval = useAuthStore((s) => s.showPendingApproval);
  const error = useAuthStore((s) => s.error);
  const bootstrap = useAuthStore((s) => s.bootstrap);
  const logout = useAuthStore((s) => s.logout);
  const clearError = useAuthStore((s) => s.clearError);
  const refreshUserProfile = useAuthStore((s) => s.refreshUserProfile);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  if (isBootstrapping) {
    return (
      <Centered>
        <ActivityIndicator size="large" color={theme.colors.primary} />
      </Centered>
    );
  }

  if (bootstrapError) {
    return (
      <Centered>
        <Text style={styles.title}>Connection problem</Text>
        <Text style={styles.message}>{bootstrapError.userMessage}</Text>
        <TouchableOpacity style={styles.button} onPress={bootstrap}>
          <Text style={styles.buttonText}>Retry</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={logout}>
          <Text style={styles.link}>Log out</Text>
        </TouchableOpacity>
      </Centered>
    );
  }

  return (
    <NavigationContainer>
      {isAuthenticated && error ? <ErrorBanner error={error} onDismiss={clearError} onRetry={refreshUserProfile} /> : null}
      {showPendingApproval ? (
        <PendingApprovalScreen />
      ) : !isAuthenticated ? (
        <AuthNavigator />
      ) : (
        <AppNavigator />
      )}
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: theme.spacing.lg,
    backgroundColor: theme.colors.background,
  },
  title: { fontSize: 20, fontWeight: '700', color: theme.colors.text.primary, marginBottom: theme.spacing.sm },
  message: { fontSize: 14, color: theme.colors.text.secondary, textAlign: 'center', marginBottom: theme.spacing.lg },
  button: {
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.md,
    paddingHorizontal: theme.spacing.xl,
    borderRadius: theme.radius.md,
    marginBottom: theme.spacing.md,
  },
  buttonText: { color: theme.colors.onPrimary, fontSize: 16, fontWeight: '600' },
  link: { color: theme.colors.primary, fontSize: 14, fontWeight: '600' },
});
