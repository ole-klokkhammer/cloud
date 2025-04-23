import { FlatList, Image, TouchableOpacity, View } from 'react-native';
import { ThemedText } from '@/components/ui/theme/ThemedText';
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
          <View style={styles.chatTextContainer}>
            <ThemedText style={styles.chatName}>{item.name}</ThemedText>
            <ThemedText style={styles.chatLastMessage}>{item.lastMessage}</ThemedText>
          </View>
        </TouchableOpacity>
      )}
    />
  );
}
