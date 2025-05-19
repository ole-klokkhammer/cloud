import { ThemedText } from '@/components/ui/text/ThemedText';
import { ThemedView } from '@/components/ui/view/ThemedView';
import { FlatList, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { styles } from './home.screen.styles';

const chats = [
    { id: 'kubernetes', name: 'Kubernetes', lastMessage: 'Error in bluetooth-bridge' },
    { id: 'frigate', name: 'Frigate', lastMessage: 'Theres a cat in the hallway' },
    { id: 'sensors', name: 'Sensors', lastMessage: 'High co2 in the livingroom.' },
];

export const HomeScreen = () => {
    const router = useRouter();

    const onPressChat = (id: string) => {
        router.push(`/chat/${id}`);
    }

    return <FlatList
        data={chats}
        keyExtractor={item => item.id}
        ListHeaderComponent={
            <Image
                source={require('@/assets/images/neo/neo_v2.png')}
                style={styles.pageHeaderLogo}
                resizeMode="cover"
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