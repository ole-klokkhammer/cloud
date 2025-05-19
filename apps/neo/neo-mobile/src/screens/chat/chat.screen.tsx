import { v4 as uuidv4 } from 'uuid';
import { FlatList, KeyboardAvoidingView, Platform } from "react-native";
import { useChatStyles } from "./chat.screen.styles"
import { ThemedView } from "@/common/components/view/ThemedView";
import { ThemedText } from "@/common/components/text/ThemedText";
import { ThemedInput } from "@/common/components/input/ThemedInput";
import { ThemedButton } from "@/common/components/button/ThemedButton";
import React, { useEffect, useState } from "react";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { useMqttSubscription } from "@/common/hooks/mqtt/useMqttSubscription";

const messageData: ChatMessage[] = [
    { id: '1', text: 'Hello!', sender: 'other' },
    { id: '2', text: 'Hi there!', sender: 'me' },
]

export type ChatMessage = {
    id: string;
    text: string;
    sender: 'me' | 'other';
};


export default function ChatScreen() {
    const styles = useChatStyles();
    const navigation = useNavigation();
    const { id } = useLocalSearchParams<{ id: string }>();
    const [messages, setMessages] = useState<ChatMessage[]>(messageData);
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
                    onChangeText={onInputChange}
                    placeholder="Type a message..."
                />
                <ThemedButton title="Send" onPress={onSendMessage} />
            </ThemedView>
        </KeyboardAvoidingView>
    );
}