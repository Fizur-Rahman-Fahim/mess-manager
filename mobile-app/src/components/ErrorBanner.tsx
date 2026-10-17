import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
// import { useQueryClient } from '@tanstack/react-query';
import { useIsFetching, useQueryClient } from '@tanstack/react-query';
import { NormalizedError } from '../utils/errorNormalizer';
import { theme } from '../theme/colors';

export interface ErrorBannerProps {
  error: NormalizedError | null;
  onDismiss?: () => void;
  /** Optional custom retry. Without it the banner re-fetches every failed query. */
  onRetry?: () => void;
}

// Network failures (0), timeouts (408), rate limits (429) and server errors (5xx) are worth retrying.
const isRetryableStatus = (status: number) =>
  status === 0 || status === 408 || status === 429 || status >= 500;

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ error, onDismiss, onRetry }) => {
  const queryClient = useQueryClient();
  const isRetrying = useIsFetching() > 0;

  if (!error) {
    return null;
  }

  const failedQueries = queryClient
    .getQueryCache()
    .findAll({ predicate: (query) => query.state.status === 'error' });

  const retry =
    onRetry ??
    (isRetryableStatus(error.status) && failedQueries.length > 0
      ? () => {
          // Clear a failed mutation shown in this banner (e.g. a meal toggle), then re-fetch failed queries.
          onDismiss?.();
          queryClient.refetchQueries({ predicate: (query) => query.state.status === 'error' });
        }
      : undefined);  

  return (
    <View style={styles.container} accessibilityRole="alert" accessibilityLiveRegion="assertive">
      <View style={styles.content}>
        <Text style={styles.message}>{error.userMessage}</Text>
        <View style={styles.actions}>
          {retry && (
            <TouchableOpacity
              onPress={retry}
              disabled={isRetrying}
              style={[styles.button, isRetrying && styles.buttonDisabled]}
              accessibilityRole="button"
              accessibilityLabel="Retry loading"
              accessibilityState={{ disabled: isRetrying, busy: isRetrying }}
            >
              <Text style={styles.buttonText}>{isRetrying ? 'Retrying…' : 'Retry'}</Text>
            </TouchableOpacity>
          )}
          {onDismiss && (
            <TouchableOpacity
              onPress={onDismiss}
              style={styles.button}
              accessibilityRole="button"
              accessibilityLabel="Dismiss error message"
            >
              <Text style={styles.buttonText}>Dismiss</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: theme.colors.error,
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  content: {
    gap: theme.spacing.sm,
  },
  message: {
    color: theme.colors.onError,
    fontSize: 14,
    fontWeight: '500',
  },
  actions: {
    flexDirection: 'row',
    gap: theme.spacing.md,
  },
  button: {
    paddingVertical: theme.spacing.xs,
    paddingHorizontal: theme.spacing.md,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: theme.radius.sm,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: theme.colors.onError,
    fontSize: 12,
    fontWeight: '600',
  },
});
