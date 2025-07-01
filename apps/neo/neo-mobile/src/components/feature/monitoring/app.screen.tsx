import { v4 as uuidv4 } from 'uuid';
import { FlatList, KeyboardAvoidingView, Platform } from "react-native";
import React, { useEffect, useState } from "react";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { useMqttSubscription } from "@/hooks/mqtt/useMqttSubscription";
import { useChatStyles } from './app.screen.styles';
import { AppTextInput } from '@/components/ui/input/input';
import { AppContainer } from '@/components/ui/container/container';
import { AppButton } from '@/components/ui/button/button';
import { AppText } from '@/components/ui/text/text';

export type ChatMessage = {
    id: string;
    text: string;
    sender: 'me' | 'other';
};

export default function MonitoringAppScreen() {
    const styles = useChatStyles();
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
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={80}
        >
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={item => item.id}
                renderItem={({ item }) => (
                    <AppContainer
                        style={[
                            styles.message,
                            item.sender === 'me' ? styles.myMessage : styles.otherMessage,
                        ]}
                    >
                        <AppText style={styles.messageText}>{item.text}</AppText>
                    </AppContainer>
                )}
                contentContainerStyle={styles.messagesContainer}
            />
            <AppContainer style={styles.inputContainer}>
                <AppTextInput
                    style={styles.input}
                    value={input}
                    onChangeText={onInputChange}
                    placeholder="Type a message..."
                />
                <AppButton title="Send" onPress={onSendMessage} />
            </AppContainer>
        </KeyboardAvoidingView>
    );
}