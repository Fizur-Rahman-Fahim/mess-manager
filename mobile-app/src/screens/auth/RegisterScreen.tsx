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

const schema = z
  .object({
    mobile_number: z.string().regex(/^\d{10,15}$/, 'Enter a valid mobile number (at least 10 digits)'),
    full_name: z.string().min(1, 'Full name is required'),
    password1: z.string().min(6, 'Password must be at least 6 characters'),
    password2: z.string().min(1, 'Confirm your password'),
  })
  .refine((data) => data.password1 === data.password2, {
    message: 'Passwords do not match',
    path: ['password2'],
  });

interface RegisterScreenProps {
  onNavigateToLogin?: () => void;
}

export const RegisterScreen: React.FC<RegisterScreenProps> = ({ onNavigateToLogin }) => {
  const { register, isLoading, error, clearError } = useAuthStore();
  const { control, handleSubmit, setError } = useForm({
    defaultValues: { mobile_number: '', full_name: '', password1: '', password2: '' },
  });

  const onSubmit = handleSubmit(async (values) => {
    const parsed = schema.safeParse(values);
    if (!parsed.success) {
      parsed.error.issues.forEach((issue) => {
        const field = String(issue.path[0]);
        setError(field as 'mobile_number' | 'full_name' | 'password1' | 'password2', {
          message: issue.message,
        });
      });
      return;
    }
    clearError();
    try {
      await register(parsed.data);
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
        <Text style={styles.title}>Create account</Text>
        <Text style={styles.subtitle}>A Super Manager must approve you before login.</Text>

        <Controller
          control={control}
          name="full_name"
          render={({ field, fieldState }) => (
            <FormField
              label="Full name"
              value={field.value}
              onChangeText={field.onChange}
              error={fieldState.error?.message}
            />
          )}
        />
        <Controller
          control={control}
          name="mobile_number"
          render={({ field, fieldState }) => (
            <FormField
              label="Mobile number"
              value={field.value}
              onChangeText={field.onChange}
              keyboardType="phone-pad"
              error={fieldState.error?.message}
            />
          )}
        />
        <Controller
          control={control}
          name="password1"
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
        <Controller
          control={control}
          name="password2"
          render={({ field, fieldState }) => (
            <FormField
              label="Confirm password"
              value={field.value}
              onChangeText={field.onChange}
              secureTextEntry
              error={fieldState.error?.message}
            />
          )}
        />

        {error ? <Text style={styles.error}>{error.userMessage}</Text> : null}
        {error?.fieldErrors
          ? Object.entries(error.fieldErrors).map(([key, messages]) => (
              <Text key={key} style={styles.error}>
                {key}: {messages.join(' ')}
              </Text>
            ))
          : null}

        <TouchableOpacity
          style={[styles.button, isLoading && styles.buttonDisabled]}
          accessibilityRole="button"
 accessibilityLabel="Create account"
 onPress={onSubmit}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color={theme.colors.onPrimary} />
          ) : (
            <Text style={styles.buttonText}>Register</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity accessibilityRole="button"
 accessibilityLabel="Back to login"
 onPress={onNavigateToLogin} style={styles.linkWrap}>
          <Text style={styles.footerLink}>Back to login</Text>
        </TouchableOpacity>
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
  title: { fontSize: 28, fontWeight: '700', color: theme.colors.text.primary, marginBottom: theme.spacing.sm },
  subtitle: { fontSize: 14, color: theme.colors.text.secondary, marginBottom: theme.spacing.lg },
  button: {
    backgroundColor: theme.colors.primary,
    paddingVertical: theme.spacing.md,
    borderRadius: theme.radius.md,
    alignItems: 'center',
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: theme.colors.onPrimary, fontSize: 16, fontWeight: '600' },
  linkWrap: { marginTop: theme.spacing.lg, alignItems: 'center' },
  footerLink: { fontSize: 14, color: theme.colors.primary, fontWeight: '600' },
  error: { color: theme.colors.error, marginBottom: theme.spacing.sm, fontSize: 14 },
});
