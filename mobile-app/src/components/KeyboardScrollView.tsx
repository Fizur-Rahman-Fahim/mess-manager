import React from 'react';
import { KeyboardAvoidingView, ScrollView, ScrollViewProps, StyleSheet } from 'react-native';

/**
 * ScrollView that stays visible above the on-screen keyboard.
 * If you ever see an extra gap above the keyboard on Android, change `behavior` to
 * `Platform.OS === 'ios' ? 'padding' : undefined` (the window is already resizing).
 */
export const KeyboardScrollView: React.FC<ScrollViewProps> = ({ children, ...props }) => (
  <KeyboardAvoidingView style={styles.flex} behavior="padding">
    <ScrollView keyboardShouldPersistTaps="handled" keyboardDismissMode="on-drag" {...props}>
      {children}
    </ScrollView>
  </KeyboardAvoidingView>
);

const styles = StyleSheet.create({
  flex: { flex: 1 },
});
