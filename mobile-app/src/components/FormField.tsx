import React from 'react';
import { Text, TextInput, StyleSheet, View } from 'react-native';
import { theme } from '../theme/colors';

interface Props {
  label: string;
  value: string;
  onChangeText: (value: string) => void;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'numeric' | 'phone-pad' | 'email-address';
  multiline?: boolean;
  error?: string;
  placeholder?: string;
}

export const FormField: React.FC<Props> = ({
  label,
  value,
  onChangeText,
  secureTextEntry,
  keyboardType,
  multiline,
  error,
  placeholder,
}) => (
  <View style={styles.field}>
    <Text style={styles.label}>{label}</Text>
    <TextInput
      style={[styles.input, multiline && styles.multiline]}
      value={value}
      onChangeText={onChangeText}
      secureTextEntry={secureTextEntry}
      keyboardType={keyboardType}
      multiline={multiline}
      placeholder={placeholder}
      autoCapitalize="none"
      accessibilityLabel={label}
    />
    {error ? (
      <Text style={styles.error} accessibilityLiveRegion="polite">
        {error}
      </Text>
    ) : null}
  </View>
);

const styles = StyleSheet.create({
  field: {
    marginBottom: theme.spacing.md,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: theme.colors.text.primary,
    marginBottom: theme.spacing.sm,
  },
  input: {
    borderWidth: 1,
    borderColor: theme.colors.border,
    borderRadius: theme.radius.md,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.md,
    fontSize: 16,
    color: theme.colors.text.primary,
    backgroundColor: theme.colors.surface,
  },
  multiline: {
    minHeight: 90,
    textAlignVertical: 'top',
  },
  error: {
    marginTop: 4,
    color: theme.colors.error,
    fontSize: 12,
  },
});
