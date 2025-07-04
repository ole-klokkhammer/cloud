import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Tabs } from 'expo-router';
import { Pressable } from 'react-native';

export default function TabLayout() {
    return (
        <Tabs screenOptions={{ headerShown: false }}>
            <Tabs.Screen
                name="index"
                options={{
                    title: 'Home',
                    tabBarIcon: ({ color }) => <FontAwesome size={28} name="home" color={color} />,
                }}
            />
            <Tabs.Screen
                name="monitoring"
                options={{
                    title: 'Monitoring',
                    tabBarIcon: ({ color }) => <FontAwesome size={28} name="cog" color={color} />,
                }}
            />
            <Tabs.Screen
                name="surveillance"
                options={{
                    title: 'Surveillance',
                    headerShown: false,
                    tabBarIcon: ({ color }) => <FontAwesome size={28} name="user" color={color} />,
                }}
            />
            <Tabs.Screen
                name="account"
                options={{
                    title: 'Account',
                    tabBarIcon: ({ color }) => <FontAwesome size={28} name="user" color={color} />,
                }}
            />
        </Tabs>
    );
} 