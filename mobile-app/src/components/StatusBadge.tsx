import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { theme } from '../theme/colors';

const statusColor = (status: string) => {
  const key = status.toLowerCase();
  if (key.includes('pending')) return theme.colors.badge.pending;
  if (key.includes('approved') || key.includes('resolved')) return theme.colors.badge.approved;
  if (key.includes('reject')) return theme.colors.badge.rejected;
  if (key.includes('progress') || key.includes('open')) return theme.colors.badge.open;
  return theme.colors.badge.open;
};

export const StatusBadge: React.FC<{ status: string; label?: string }> = ({ status, label }) => (
  <View style={[styles.badge, { backgroundColor: statusColor(status) }]}>
    <Text style={styles.text}>{label || status.replace('_', ' ')}</Text>
  </View>
);

const styles = StyleSheet.create({
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: theme.spacing.sm,
    paddingVertical: 4,
    borderRadius: theme.radius.full,
  },
  text: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'capitalize',
  },
});
