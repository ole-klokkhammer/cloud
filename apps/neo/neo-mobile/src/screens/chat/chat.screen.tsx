import { FlatList, KeyboardAvoidingView, Platform } from "react-native";
import { useChatStyles } from "./chat.screen.styles"
import { ThemedView } from "@/components/view/ThemedView";
import { ThemedText } from "@/components/text/ThemedText";
import { ThemedInput } from "@/components/input/ThemedInput";
import { ThemedButton } from "@/components/button/ThemedButton";

export default function ChatScreen({ messages, input, setInput, sendMessage }) {
    const styles = useChatStyles();
    return <KeyboardAvoidingView
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
        ;
}