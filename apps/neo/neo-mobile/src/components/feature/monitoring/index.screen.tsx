import { AppText } from '@/components/ui/text/text';
import { AppContainer } from '@/components/ui/container/container';
import { FlatList, Image, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useNavigation } from '@react-navigation/native';
import { useMqttSubscription } from '@/hooks/mqtt/useMqttSubscription';
import React from 'react';
import { styles } from './index.screen.styles';

type App = {
    id: string;
    name: string;
    lastMessage: string;
}

export const MonitoringScreen = () => {
    const router = useRouter();
    const [apps, setApps] = React.useState<App[]>([]);

    const onPressChat = (id: string) => {
        router.push(`/monitoring/${id}`);
    }

    useMqttSubscription('logs/kubernetes/errors/#', (topic, _) => {
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
                <AppContainer style={styles.chatTextContainer}>
                    <AppText style={styles.chatName}>{item.name}</AppText>
                    <AppText style={styles.chatLastMessage}>{item.lastMessage}</AppText>
                </AppContainer>
            </TouchableOpacity>
        )}
    />
}