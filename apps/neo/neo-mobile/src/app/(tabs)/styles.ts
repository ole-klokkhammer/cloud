import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
    chatsContainer: {
        marginTop: 16,
        gap: 8,
        paddingBottom: 32,
    },
    chatItem: {
        paddingVertical: 12,
        paddingHorizontal: 8,
        borderBottomWidth: 1,
        borderColor: '#eee',
    },
    lastMessage: {
        color: '#888',
        fontSize: 13,
        marginTop: 2,
    },
    reactLogo: {
        height: 250,
        width: '100%',
        resizeMode: 'contain',
        alignSelf: 'center',
        marginBottom: 16,
    },
});