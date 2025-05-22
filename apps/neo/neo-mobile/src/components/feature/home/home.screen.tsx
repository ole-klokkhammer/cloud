import { ThemedText } from '@/components/ui/text/ThemedText';
import { ThemedView } from '@/components/ui/view/ThemedView';
import { FlatList, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { styles } from './home.screen.styles';
import { useMqttSubscription } from '@/hooks/mqtt/useMqttSubscription';
import React from 'react';

type App = {
    id: string;
    name: string;
    lastMessage: string;
}

export const HomeScreen = () => {
    const router = useRouter();
    const [apps, setApps] = React.useState<App[]>([]);

    const onPressChat = (id: string) => {
        router.push(`/chat/${id}`);
    }

    useMqttSubscription('neo/stream/error/#', (topic, _) => {
        console.log('Received message:', topic);
        const header = topic.split('/')[3];

        // Check if the app with the same id already exists
        setApps((prevApps) => {
            if (prevApps.some(app => app.id === header)) {
                return prevApps; // app is already there
            } else {
                return [...prevApps, {
                    id: header,
                    name: header,
                    lastMessage: 'Error in app',
                }];
            }
        });
    });

    return <FlatList
        data={apps}
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