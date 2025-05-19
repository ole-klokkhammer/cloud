import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
    pageHeaderLogo: {
        width: '100%',
        height: 300,
        alignSelf: 'center',
        marginBottom: 8,
    },
    chatListContainer: {
        marginTop: 20,
        gap: 10,
        paddingBottom: 20,
    },
    chatItem: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 12,
        paddingHorizontal: 16,
        borderBottomWidth: 1,
        borderRadius: 8,
        marginHorizontal: 8,
        marginBottom: 4,
    },
    chatAvatar: {
        width: 48,
        height: 48,
        borderRadius: 24,
        marginRight: 14,
    },
    chatTextContainer: {
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'center',
    },
    chatName: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 2,
    },
    chatLastMessage: {
        fontSize: 14,
        color: '#888',
    }
});