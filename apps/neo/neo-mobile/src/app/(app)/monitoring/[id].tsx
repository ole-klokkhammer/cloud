import { v4 as uuidv4 } from 'uuid';
import { AppButton } from '@/components/ui/button/button';
import { AppTextInput } from '@/components/ui/input/input';
import { Container } from '@/components/ui/layout/container';
import { Page } from '@/components/ui/layout/page';
import { AppText } from '@/components/ui/text/text';
import { useMqttSubscription } from '@/hooks/mqtt/useMqttSubscription';
import { useLocalSearchParams, useNavigation } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform } from 'react-native';

export type ChatMessage = {
  id: string;
  text: string;
  sender: 'me' | 'other';
};

export default function MonitorApp() {
  const navigation = useNavigation();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const flatListRef = React.useRef<FlatList<ChatMessage>>(null);

  const clearInput = () => onInputChange('');
  const onInputChange = (text: string) => setInput(text);

  const onSendMessage = () => {
    if (input.trim().length > 0) {
      setMessages([
        ...messages,
        { id: Date.now().toString(), text: input, sender: 'me' },
      ]);
      clearInput();
    }
  };

  useEffect(() => {
    navigation.setOptions({ title: `${id}` });
  }, [navigation]);

  useMqttSubscription(`logs/kubernetes/errors/${id}`, (_, message) => {
    const newMessage: ChatMessage = {
      id: uuidv4(),
      text: message.toString(),
      sender: 'other',
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  });

  React.useEffect(() => {
    if (flatListRef?.current && messages.length > 0) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: false });
      }, 0);
    }
  }, [messages]);

  return (
    <Page>
      <KeyboardAvoidingView
        className="flex-1"
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={80}
      >
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={item => item.id}
          renderItem={({ item }) => (
            <Container
              className={[
                "my-1.5 py-2.5 px-4 rounded-xl max-w-[80%] shadow",
                item.sender === 'other'
                  ? "bg-gray-800 dark:bg-gray-700 self-start rounded-bl-[6px]"
                  : "bg-blue-600 dark:bg-blue-500 self-end rounded-br-[6px]"
              ].filter(Boolean).join(' ')}
            >
              <AppText className='font-m'>{item.text}</AppText>
            </Container>
          )}
          contentContainerClassName='p-12 pb-4'
        />
        <Container className='flex-row p-2.5 border-t border-t-gray-200 dark:border-t-zinc-800 bg-white dark:bg-zinc-900 items-center'>
          <AppTextInput
            className='flex-1 border rounded-2xl px-4 py-2 mr-2 text-base'
            value={input}
            onChangeText={onInputChange}
            placeholder="Type a message..."
          />
          <AppButton title="Send" onPress={onSendMessage} />
        </Container>
      </KeyboardAvoidingView>
    </Page>
  );
}