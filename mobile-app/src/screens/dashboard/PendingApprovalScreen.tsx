import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, SafeAreaView } from 'react-native';
import { useAuthStore } from '../../stores/authStore';
import { theme } from '../../theme/colors';

export const PendingApprovalScreen: React.FC = () => {
  const { pendingMobile, dismissPending } = useAuthStore();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>Pending approval</Text>
        <Text style={styles.subtitle}>
          Your account is awaiting Super Manager approval. You cannot sign in until it is activated.
        </Text>
        {pendingMobile ? (
          <View style={styles.details}>
            <Text style={styles.label}>Mobile</Text>
            <Text style={styles.value}>{pendingMobile}</Text>
          </View>
        ) : null}
        <Text style={styles.message}>
          After approval, return to login and sign in with this mobile number.
        </Text>
        <TouchableOpacity style={styles.button} accessibilityRole="button"
 accessibilityLabel="Back to login"
 onPress={dismissPending}>
          <Text style={styles.buttonText}>Back to login</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  content: {
    flex: 1,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  details: {
    backgroundColor: theme.colors.surface,
    borderRadius: theme.radius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  label: { fontSize: 12, color: theme.colors.text.tertiary, marginBottom: theme.spacing.xs },
  value: { fontSize: 16, fontWeight: '500', color: theme.colors.text.primary },
  message: {
    fontSize: 14,
    color: theme.colors.text.secondary,
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: theme.spacing.xl,
  },
  button: {
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.radius.md,
    alignItems: 'center',
  },
  buttonText: { color: theme.colors.onPrimary, fontSize: 16, fontWeight: '600' },
});
