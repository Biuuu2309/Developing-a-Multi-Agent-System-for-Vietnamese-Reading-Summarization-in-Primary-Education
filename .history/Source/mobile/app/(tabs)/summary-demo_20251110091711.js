import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { useThemeColor } from '@/hooks/use-theme-color';
import { messageService } from '@/services/api';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function SummaryDemo() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [userId] = useState('557fd328-83f0-4231-80df-ff6f4a289d03'); // Thay bằng user ID thực tế
  const flatListRef = useRef(null);

  const backgroundColor = useThemeColor({}, 'background');
  const textColor = useThemeColor({}, 'text');
  const tintColor = useThemeColor({}, 'tint');

  useEffect(() => {
    initializeConversation();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (messages.length > 0 && flatListRef.current) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  const initializeConversation = async () => {
    try {
      const conversation = await messageService.createConversation(userId, 'Summary Chat');
      setConversationId(conversation.conversation_id || conversation.id);
      loadMessages(conversation.conversation_id || conversation.id);
    } catch (error) {
      console.error('Error initializing conversation:', error);
      Alert.alert('Error', 'Không thể khởi tạo cuộc trò chuyện');
    }
  };

  const loadMessages = async (convId) => {
    try {
      const msgs = await messageService.getMessagesByConversation(convId);
      setMessages(msgs || []);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || !conversationId || isLoading) return;

    const userMessage = {
      messageId: `temp-${Date.now()}`,
      conversationId,
      userId,
      role: 'USER',
      content: inputText.trim(),
      status: 'PENDING',
      createdAt: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await messageService.createMessage(
        conversationId,
        userId,
        inputText.trim()
      );

      if (response && response.messageId) {
        await loadMessages(conversationId);
      } else {
        throw new Error('Invalid response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      Alert.alert('Error', 'Không thể gửi tin nhắn. Vui lòng thử lại.');
      setMessages((prev) => prev.filter((msg) => msg.messageId !== userMessage.messageId));
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = ({ item }) => {
    const isUser = item.role === 'USER';
    const isAssistant = item.role === 'ASSISTANT';
    const isPending = item.status === 'PENDING' || item.status === 'PROCESSING';

    return (
      <View
        style={[
          styles.messageContainer,
          isUser && styles.userMessageContainer,
          isAssistant && styles.assistantMessageContainer,
        ]}>
        <View
          style={[
            styles.messageBubble,
            isUser && styles.userBubble,
            isAssistant && styles.assistantBubble,
            isPending && styles.pendingBubble,
          ]}>
          {isPending && isUser ? (
            <View style={styles.pendingContainer}>
              <ActivityIndicator size="small" color={isUser ? '#fff' : tintColor} />
              <ThemedText style={[styles.messageText, isUser && styles.userMessageText]}>
                Đang gửi...
              </ThemedText>
            </View>
          ) : isPending && isAssistant ? (
            <View style={styles.pendingContainer}>
              <ActivityIndicator size="small" color={tintColor} />
              <ThemedText style={styles.messageText}>Đang xử lý...</ThemedText>
            </View>
          ) : (
            <ThemedText style={[styles.messageText, isUser && styles.userMessageText]}>
              {item.content}
            </ThemedText>
          )}
        </View>
      </View>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor }]} edges={['top']}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}>
        <View style={styles.header}>
          <ThemedText type="subtitle" style={styles.headerTitle}>
            MAS Summary Chat
          </ThemedText>
        </View>

        <FlatList
          ref={flatListRef}
          data={messages}
          renderItem={renderMessage}
          keyExtractor={(item, index) => item.messageId || `msg-${index}`}
          contentContainerStyle={styles.messagesList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <ThemedText style={styles.emptyText}>
                Xin chào! Tôi có thể giúp bạn tóm tắt văn bản. Hãy gửi văn bản bạn muốn tóm tắt.
              </ThemedText>
            </View>
          }
        />

        <View style={[styles.inputContainer, { backgroundColor }]}>
          <TextInput
            style={[styles.textInput, { color: textColor, borderColor: tintColor }]}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Nhập tin nhắn..."
            placeholderTextColor={textColor + '80'}
            multiline
            maxLength={5000}
            editable={!isLoading && !!conversationId}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              { backgroundColor: '#007eff' },
              (!inputText.trim() || isLoading || !conversationId) && styles.sendButtonDisabled,
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading || !conversationId}>
            {isLoading ? (
              <ActivityIndicator size="small" color="#fff" />
            ) : (
              <ThemedText style={styles.sendButtonText}>Gửi</ThemedText>
            )}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    textAlign: 'center',
  },
  messagesList: {
    padding: 16,
    paddingBottom: 8,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  emptyText: {
    textAlign: 'center',
    opacity: 0.6,
    fontSize: 16,
  },
  messageContainer: {
    marginBottom: 12,
    flexDirection: 'row',
  },
  userMessageContainer: {
    justifyContent: 'flex-end',
  },
  assistantMessageContainer: {
    justifyContent: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 18,
    
  },
  userBubble: {
    backgroundColor: '#007AFF',
    alignSelf: 'flex-end',
    borderBottomRightRadius: 4,
  },
  assistantBubble: {
    backgroundColor: '#E5E5EA',
    alignSelf: 'flex-start',
    borderBottomLeftRadius: 4,
  },
  pendingBubble: {
    opacity: 0.7,
  },
  messageText: {
    fontSize: 16,
    lineHeight: 20,
  },
  userMessageText: {
    color: '#fff',
  },
  pendingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    alignItems: 'flex-end',
    gap: 8,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxHeight: 100,
    fontSize: 16,
  },
  sendButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
    minWidth: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonDisabled: {
    opacity: 0.5,
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: '600',
    fontSize: 16,
  },
});
