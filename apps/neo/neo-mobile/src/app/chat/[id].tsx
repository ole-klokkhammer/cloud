import { v4 as uuidv4 } from 'uuid';
import React, { useEffect, useState } from 'react';
import { useNavigation } from 'expo-router';
import ChatScreen, { ChatMessage } from '@/views/screens/chat/chat.screen';
import { useMqttSubscription } from '@/hooks/mqtt/useMqttSubscription';
import { useLocalSearchParams } from 'expo-router/build/hooks';

const messageData: ChatMessage[] = [
  { id: '1', text: 'Hello!', sender: 'other' },
  { id: '2', text: 'Hi there!', sender: 'me' },
]

export default function Chat() {
  const navigation = useNavigation();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [messages, setMessages] = useState<ChatMessage[]>(messageData);
  const [input, setInput] = useState('');

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
    navigation.setOptions({ title: `Chat with test` });
  }, [navigation]);


  useMqttSubscription('neo/stream/' + id, (_, message) => {
    const newMessage: ChatMessage = {
      id: uuidv4(),
      text: message.toString(),
      sender: 'other',
    };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
  });


  return <ChatScreen
    autoscroll={true}
    messages={messages}
    input={input}
    onInputChange={onInputChange}
    onSendMessage={onSendMessage}
  />;
}