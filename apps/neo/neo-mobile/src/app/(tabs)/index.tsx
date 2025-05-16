import { HomeScreen } from '@/screens/home/home.screen';
import { useRouter } from 'expo-router';

const streams = [
  { id: 'kubernetes', name: 'Kubernetes', lastMessage: 'Error in bluetooth-bridge' },
  { id: 'frigate', name: 'Frigate', lastMessage: 'Theres a cat in the hallway' },
  { id: 'sensors', name: 'Sensors', lastMessage: 'High co2 in the livingroom.' },
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
