import { FlatList, Image, TouchableOpacity, View } from 'react-native';
import { ThemedText } from '@/components/ui/text/ThemedText';
import { useRouter } from 'expo-router';
import { styles } from './styles';
import { ThemedView } from '@/components/ui/view/ThemedView';
import MatrixBackground from '@/components/ui/background/MatrixBackground';

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
          source={require('@/assets/images/neo/neo_v2.png')}
          style={styles.pageHeaderLogo}
        />
      }
      contentContainerStyle={styles.chatListContainer}
      renderItem={({ item }) => (
        <TouchableOpacity
          style={styles.chatItem}
          onPress={() => router.push(`/chat/${item.id}`)}
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
  );
}
