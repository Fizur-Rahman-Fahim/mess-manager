import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { Controller, useForm } from 'react-hook-form';
import { z } from 'zod';
import { useAuthStore } from '../../stores/authStore';
import { theme } from '../../theme/colors';
import { FormField } from '../../components/FormField';
import { isRateLimitError } from '../../utils/errorNormalizer';

const schema = z.object({
  mobile_number: z.string().regex(/^\d{10,15}$/, 'Enter a valid mobile number'),
  password: z.string().min(1, 'Password is required'),
});

interface LoginScreenProps {
  onNavigateToRegister?: () => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onNavigateToRegister }) => {
  const { login, isLoading, error, clearError } = useAuthStore();
  const { control, handleSubmit, setError } = useForm({
    defaultValues: { mobile_number: '', password: '' },
  });

  const onSubmit = handleSubmit(async (values) => {
    const parsed = schema.safeParse(values);
    if (!parsed.success) {
      parsed.error.issues.forEach((issue) => {
        const field = issue.path[0];
        if (field === 'mobile_number' || field === 'password') {
          setError(field, { message: issue.message });
        }
      });
      return;
    }
    clearError();
    try {
      await login(parsed.data.mobile_number, parsed.data.password);
    } catch {
      // store holds error
    }
  });

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <Text style={styles.title}>Mass Manager</Text>
          <Text style={styles.subtitle}>Sign in with your mobile number</Text>
        </View>

        <Controller
          control={control}
          name="mobile_number"
          render={({ field, fieldState }) => (
            <FormField
              label="Mobile number"
              value={field.value}
              onChangeText={field.onChange}
              keyboardType="phone-pad"
              placeholder="01XXXXXXXXX"
              error={fieldState.error?.message}
            />
          )}
        />
        <Controller
          control={control}
          name="password"
          render={({ field, fieldState }) => (
            <FormField
              label="Password"
              value={field.value}
              onChangeText={field.onChange}
              secureTextEntry
              error={fieldState.error?.message}
            />
          )}
        />

        {error ? (
          <Text style={styles.error}>
            {isRateLimitError(error)
              ? error.userMessage
              : error.errorCode === 'PENDING_APPROVAL'
                ? error.userMessage
                : error.userMessage}
          </Text>
        ) : null}

        <TouchableOpacity
          style={[styles.button, isLoading && styles.buttonDisabled]}
          accessibilityRole="button"
 accessibilityLabel="Log in"
 onPress={onSubmit}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={theme.colors.onPrimary} />
          ) : (
            <Text style={styles.buttonText}>Login</Text>
          )}
        </TouchableOpacity>

        <View style={styles.footer}>
          <Text style={styles.footerText}>Don&apos;t have an account? </Text>
          <TouchableOpacity accessibilityRole="button"
 accessibilityLabel="Go to register"
 onPress={onNavigateToRegister}>
            <Text style={styles.footerLink}>Register</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.background },
  content: {
    flexGrow: 1,
    paddingHorizontal: theme.spacing.lg,
    paddingVertical: theme.spacing.xl,
    justifyContent: 'center',
  },
  header: { marginBottom: theme.spacing.xl },
  title: { fontSize: 28, fontWeight: '700', color: theme.colors.text.primary, marginBottom: theme.spacing.sm },
  subtitle: { fontSize: 16, color: theme.colors.text.secondary },
  button: {
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.radius.md,
    alignItems: 'center',
    marginTop: theme.spacing.sm,
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: theme.colors.onPrimary, fontSize: 16, fontWeight: '600' },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: theme.spacing.xl },
  footerText: { fontSize: 14, color: theme.colors.text.secondary },
  footerLink: { fontSize: 14, color: theme.colors.primary, fontWeight: '600' },
  error: { color: theme.colors.error, marginBottom: theme.spacing.md, fontSize: 14 },
});
