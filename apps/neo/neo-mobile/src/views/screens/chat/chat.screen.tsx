import { FlatList, KeyboardAvoidingView, Platform } from "react-native";
import { useChatStyles } from "./chat.screen.styles"
import { ThemedView } from "@/components/view/ThemedView";
import { ThemedText } from "@/components/text/ThemedText";
import { ThemedInput } from "@/components/input/ThemedInput";
import { ThemedButton } from "@/components/button/ThemedButton";
import React from "react";

export type ChatMessage = {
    id: string;
    text: string;
    sender: 'me' | 'other';
};

export type ChatScreenProps = {
    messages: ChatMessage[];
    input: string;
    onInputChange: (text: string) => void;
    onSendMessage: () => void;
    autoscroll?: boolean
};

export default function ChatScreen(props: ChatScreenProps) {
    const { messages, input, onInputChange, onSendMessage } = props;
    const styles = useChatStyles();
    const flatListRef = React.useRef<FlatList<ChatMessage>>(null);

    if (props.autoscroll) {
        React.useEffect(() => {
            if (flatListRef?.current && messages.length > 0) {
                setTimeout(() => {
                    flatListRef.current?.scrollToEnd({ animated: false });
                }, 0);
            }
        }, [messages]);
    }

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