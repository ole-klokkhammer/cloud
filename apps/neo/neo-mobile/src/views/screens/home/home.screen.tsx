import { ThemedText } from '@/components/text/ThemedText';
import { ThemedView } from '@/components/view/ThemedView';
import { FlatList, Image, TouchableOpacity } from 'react-native';
import { styles } from './home.screen.styles';

export type HomeScreenProps = {
    chats: {
        id: string;
        name: string;
        lastMessage: string;
    }[];
    onPressChat: (id: string) => void;
}

export const HomeScreen = (props: HomeScreenProps) => {
    const { chats, onPressChat } = props;

    return <FlatList
        data={chats}
        keyExtractor={item => item.id}
        ListHeaderComponent={
            <Image
                source={require('@/assets/images/neo/neo_v2.png')}
                style={styles.pageHeaderLogo}
            />
        }
        contentContainerStyle={styles.chatListContainer}
        renderItem={({ item }) => (
            <TouchableOpacity
                style={styles.chatItem}
                onPress={() => onPressChat(item.id)}
            >
                <Image
                    source={require('@/assets/images/favicon.png')}
                    style={styles.chatAvatar}
                />
                <ThemedView style={styles.chatTextContainer}>
                    <ThemedText style={styles.chatName}>{item.name}</ThemedText>
                    <ThemedText style={styles.chatLastMessage}>{item.lastMessage}</ThemedText>
                </ThemedView>
            </TouchableOpacity>
        )}
    />
}