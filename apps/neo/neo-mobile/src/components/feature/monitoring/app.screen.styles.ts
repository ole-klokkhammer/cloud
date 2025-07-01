import { StyleSheet } from 'react-native';
import { useColorScheme } from 'react-native';

export const useChatStyles = () => {
    const colorScheme = useColorScheme();
    const isDark = colorScheme === 'dark';

    return StyleSheet.create({
        container: {
            flex: 1,
        },
        messagesContainer: {
            padding: 12,
            paddingBottom: 4,
        },
        message: {
            marginVertical: 6,
            paddingVertical: 10,
            paddingHorizontal: 16,
            borderRadius: 18,
            maxWidth: '80%',
            shadowOpacity: 0.08,
            shadowRadius: 2,
            shadowOffset: { width: 0, height: 1 },
            elevation: 1,
        },
        myMessage: {
            backgroundColor: isDark ? '#2563eb' : '#4f8cff',
            alignSelf: 'flex-end',
            borderBottomRightRadius: 6,
        },
        otherMessage: {
            backgroundColor: isDark ? '#27272a' : '#e5e7eb',
            alignSelf: 'flex-start',
            borderBottomLeftRadius: 6,
        },
        messageText: {
            fontSize: 16,
        },
        inputContainer: {
            flexDirection: 'row',
            padding: 10,
            borderTopWidth: 1,
            borderColor: isDark ? '#27272a' : '#e5e7eb',
            backgroundColor: isDark ? '#18181b' : '#fff',
            alignItems: 'center',
        },
        input: {
            flex: 1,
            borderWidth: 1,
            borderColor: isDark ? '#27272a' : '#d1d5db',
            borderRadius: 20,
            paddingHorizontal: 14,
            paddingVertical: 8,
            marginRight: 8,
            fontSize: 16,
            backgroundColor: isDark ? '#23232b' : '#f3f4f6',
            color: isDark ? '#f3f4f6' : '#222',
        },
    });
};