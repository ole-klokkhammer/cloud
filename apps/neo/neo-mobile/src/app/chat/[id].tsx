import { v4 as uuidv4 } from 'uuid';
import React, { useEffect, useState } from 'react';
import { useNavigation } from 'expo-router';
import mqtt from 'mqtt';
import ChatScreen, { ChatMessage } from '@/screens/chat/chat.screen';

const messageData: ChatMessage[] = [
  { id: '1', text: 'Hello!', sender: 'other' },
  { id: '2', text: 'Hi there!', sender: 'me' },
]

export default function Chat() {
  const navigation = useNavigation();

  const [messages, setMessages] = useState<ChatMessage[]>(messageData);
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
    const client = mqtt.connect('ws://192.168.10.207:8000/mqtt',
      { clientId: 'clientId-222', reconnectPeriod: 2000 }
    );

    client.on('connect', () => {
      console.log('Connected to MQTT broker');
    });

    client.on('close', () => {
      console.log('MQTT connection closed');
    });

    client.on('offline', () => {
      console.log('MQTT client is offline');
    });

    client.on('error', (err) => {
      console.log('MQTT error:', err);
    });

    client.on('message', (topic, message) => {
      const newMessage: ChatMessage = {
        id: uuidv4(),
        text: message.toString(),
        sender: 'other',
      };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
    });

    client.subscribe('neo/stream/kubernetes');

    return () => {
      client.end();
    };
  }, []);


  return <ChatScreen
    messages={messages}
    input={input}
    setInput={setInput}
    sendMessage={sendMessage}
  />;
}