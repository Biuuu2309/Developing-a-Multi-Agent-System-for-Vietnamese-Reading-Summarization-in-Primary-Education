import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { ThemedText } from './themed-text';
import { ThemedView } from './themed-view';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Colors } from '@/constants/theme';

export default function ChatMessage({ message, role }) {
  const colorScheme = useColorScheme();
  const isUser = role === 'USER' || role === 'user';
  const colors = Colors[colorScheme ?? 'light'];

  return (
    <View style={[
      styles.messageContainer,
      isUser ? styles.userMessage : styles.assistantMessage
    ]}>
      <View style={[
        styles.messageBubble,
        isUser ? styles.userBubble : styles.assistantBubble,
        { backgroundColor: isUser ? colors.tint : (colors.background === '#fff' ? '#f0f0f0' : '#2a2a2a') }
      ]}>
        <ThemedText style={[
          styles.messageText,
          { color: isUser ? '#fff' : colors.text }
        ]}>
          {message}
        </ThemedText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  messageContainer: {
    marginVertical: 4,
    paddingHorizontal: 16,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  assistantMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 18,
  },
  userBubble: {
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 22,
  },
});

