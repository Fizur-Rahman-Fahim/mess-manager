import { MD3LightTheme, type MD3Theme } from 'react-native-paper';
import { theme } from './colors';

export const paperTheme: MD3Theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: theme.colors.primary,
    onPrimary: theme.colors.onPrimary,
    primaryContainer: theme.colors.primaryContainer,
    onPrimaryContainer: theme.colors.onPrimaryContainer,
    secondary: theme.colors.secondary,
    onSecondary: theme.colors.onSecondary,
    error: theme.colors.error,
    onError: theme.colors.onError,
    background: theme.colors.background,
    onBackground: theme.colors.onBackground,
    surface: theme.colors.surface,
    onSurface: theme.colors.onSurface,
    outline: theme.colors.border,
  },
};
