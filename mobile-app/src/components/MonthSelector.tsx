import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { addMonths, formatMonthLabel } from '../utils/dates';
import { theme } from '../theme/colors';

interface MonthSelectorProps {
  month: string;
  onChange: (month: string) => void;
}

export const MonthSelector: React.FC<MonthSelectorProps> = ({ month, onChange }) => (
  <View style={styles.row}>
    <TouchableOpacity
      style={styles.button}
      onPress={() => onChange(addMonths(month, -1))}
      accessibilityRole="button"
      accessibilityLabel="Previous month"
    >
      <Text style={styles.chevron}>‹</Text>
    </TouchableOpacity>
    <Text style={styles.label}>{formatMonthLabel(month)}</Text>
    <TouchableOpacity
      style={styles.button}
      onPress={() => onChange(addMonths(month, 1))}
      accessibilityRole="button"
      accessibilityLabel="Next month"
    >
      <Text style={styles.chevron}>›</Text>
    </TouchableOpacity>
  </View>
);

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: theme.spacing.sm,
  },
  button: {
    paddingHorizontal: theme.spacing.md,
    paddingVertical: theme.spacing.sm,
  },
  chevron: {
    fontSize: 28,
    color: theme.colors.primary,
    fontWeight: '600',
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text.primary,
  },
});
