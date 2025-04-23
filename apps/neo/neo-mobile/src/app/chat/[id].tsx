import React, { useEffect, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { useChatStyles } from './styles';
import { ThemedView } from '@/components/ui/view/ThemedView';
import { ThemedText } from '@/components/ui/text/ThemedText';
import { ThemedInput } from '@/components/ui/input/ThemedInput';
import { ThemedButton } from '@/components/ui/button/ThemedButton';
import { useNavigation } from 'expo-router';

type Message = {
  id: string;
  text: string;
  sender: 'me' | 'other';
};

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Hello! 👋', sender: 'other' },
    { id: '2', text: 'Hi there!', sender: 'me' },
  ]);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if (input.trim().length === 0) return;
    setMessages([
      ...messages,
      { id: Date.now().toString(), text: input, sender: 'me' },
    ]);
    setInput('');
  };

  const navigation = useNavigation();
  useEffect(() => {
    navigation.setOptions({ title: `Chat with test` });
  }, [navigation]);

  const styles = useChatStyles();

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={80}
    >
      <FlatList
        data={messages}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <ThemedView
            style={[
              styles.message,
              item.sender === 'me' ? styles.myMessage : styles.otherMessage,
            ]}
          >
            <ThemedText style={styles.messageText}>{item.text}</ThemedText>
          </ThemedView>
        )}
        contentContainerStyle={styles.messagesContainer}
      />
      <ThemedView style={styles.inputContainer}>
        <ThemedInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Type a message..."
        />
        <ThemedButton title="Send" onPress={sendMessage} />
      </ThemedView>
    </KeyboardAvoidingView>
  );
}