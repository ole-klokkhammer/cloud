import { FlatList, Image, StyleSheet, TouchableOpacity, View } from 'react-native';
import { ThemedText } from '@/components/ui/text/ThemedText';
import { useRouter } from 'expo-router';
import { styles } from './styles';

const chats = [
  { id: '1', name: 'Alice', lastMessage: 'Hey, how are you?' },
  { id: '2', name: 'Bob', lastMessage: 'Let\'s catch up tomorrow.' },
  { id: '3', name: 'Charlie', lastMessage: 'See you at the meeting.' },
];


export default function HomeScreen() {
  const router = useRouter();

  return (
    <FlatList
      data={chats}
      keyExtractor={item => item.id}
      ListHeaderComponent={
        <Image
          source={require('@/assets/images/partial-react-logo.png')}
          style={styles.reactLogo}
        />
      }
      contentContainerStyle={styles.chatsContainer}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.chatItem}
          onPress={() => router.push(`/chat/${item.id}`)}
        >
          <View>
            <ThemedText type="default">{item.name}</ThemedText>
            <ThemedText type="default" style={styles.lastMessage}>
              {item.lastMessage}
            </ThemedText>
          </View>
        </TouchableOpacity>
      )}
    />
  );
}
