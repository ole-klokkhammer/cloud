import { HomeScreen } from '@/views/screens/home/home.screen';
import { useRouter } from 'expo-router';

const streams = [
  { id: '1', name: 'Kubernetes', lastMessage: 'Error in bluetooth-bridge' },
  { id: '2', name: 'Frigate', lastMessage: 'Theres a cat in the hallway' },
  { id: '3', name: 'Sensors', lastMessage: 'High co2 in the livingroom.' },
];

export default function Home() {
  const router = useRouter();

  return <HomeScreen
    chats={streams}
    onPressChat={(id) => {
      router.push(`/chat/${id}`);
    }}
  />;
}
