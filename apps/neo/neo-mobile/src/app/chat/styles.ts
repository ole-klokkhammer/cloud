import { StyleSheet } from 'react-native';


export const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#fff' },
    messagesContainer: { padding: 10 },
    message: {
        marginVertical: 4,
        padding: 10,
        borderRadius: 12,
        maxWidth: '80%',
    },
    myMessage: {
        backgroundColor: '#DCF8C6',
        alignSelf: 'flex-end',
    },
    otherMessage: {
        backgroundColor: '#ECECEC',
        alignSelf: 'flex-start',
    },
    messageText: { fontSize: 16 },
    inputContainer: {
        flexDirection: 'row',
        padding: 8,
        borderTopWidth: 1,
        borderColor: '#eee',
        backgroundColor: '#fafafa',
    },
    input: {
        flex: 1,
        borderWidth: 1,
        borderColor: '#ddd',
        borderRadius: 20,
        paddingHorizontal: 12,
        marginRight: 8,
        fontSize: 16,
        backgroundColor: '#fff',
    },
});