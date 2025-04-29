import React, { useEffect, useState } from 'react';
import { FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { useChatStyles } from '../../screens/chat/chat.screen.styles';
import { ThemedView } from '@/components/view/ThemedView';
import { ThemedText } from '@/components/text/ThemedText';
import { ThemedInput } from '@/components/input/ThemedInput';
import { ThemedButton } from '@/components/button/ThemedButton';
import { useNavigation } from 'expo-router';
import { Client, Message as MqttMessage } from 'paho-mqtt';

const messageData: Message[] = [
  { id: '1', text: 'Hello!', sender: 'other' },
  { id: '2', text: 'Hi there!', sender: 'me' },
]

type Message = {
  id: string;
  text: string;
  sender: 'me' | 'other';
};

export default function ChatScreen() {
  const navigation = useNavigation();
  const styles = useChatStyles();

  const [messages, setMessages] = useState<Message[]>(messageData);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if (input.trim().length > 0) {
      setMessages([
        ...messages,
        { id: Date.now().toString(), text: input, sender: 'me' },
      ]);
      setInput('');
    }
  };

  useEffect(() => {
    navigation.setOptions({ title: `Chat with test` });
  }, [navigation]);

  useEffect(() => {
    const useSSL = false;
    const client = new Client(
      'ws://192.168.10.207:8000/mqtt',
      'clientId-222'
    );

    client.onConnectionLost = (responseObject) => {
      if (responseObject.errorCode !== 0) {
        console.log('Connection lost:', responseObject.errorMessage);
      }
    };

    client.onMessageArrived = (message: MqttMessage) => {
      console.log(message.destinationName, message.payloadString);
    };

    client.connect({
      onSuccess: () => {
        console.log('Connected!');
        client.subscribe('frigate/#');
        const msg = new MqttMessage('Hello from React Native!');
        msg.destinationName = 'test/topic';
        client.send(msg);
      },
      useSSL,
      timeout: 3,
      onFailure: (err) => {
        console.log('Connection failed:', err);
      },
    });

    return () => {
      client.disconnect();
    };
  }, []);

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