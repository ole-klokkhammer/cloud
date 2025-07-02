import { Container } from "@/components/ui/layout/container";
import { Page } from "@/components/ui/layout/page";
import { AppText } from "@/components/ui/text/text";
import { useMqttSubscription } from "@/hooks/mqtt/useMqttSubscription";
import { useRouter } from "expo-router";
import { useState } from "react";
import { FlatList, Image, TouchableOpacity } from 'react-native';

type App = {
  id: string;
  name: string;
  lastMessage: string;
}

export default function MonitoringPage() {
  const router = useRouter();
  const [apps, setApps] = useState<App[]>([]);

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


  return (
    <Page>
      <FlatList
        data={apps}
        keyExtractor={item => item.id}
        ListHeaderComponent={
          <Image
            source={require('@/assets/images/neo/neo_v2.png')}
            className="w-full align-baseline self-center mb-2"
            resizeMode="cover"
          />
        }
        contentContainerClassName="gap-2.5 pb-5"
        renderItem={({ item }) => (
          <TouchableOpacity
            className="flex-row items-center py-3 px-4 border-b border-gray-200 rounded-lg mx-2 mb-1"
            onPress={() => onPressChat(item.id)}
          >
            <Image
              source={require('@/assets/images/favicon.png')}
              className="w-12 h-12 rounded-full mr-3"
            />
            <Container className="flex-1 flex-direction-column justify-content-center">
              <AppText className="text-base font-bold mb-0.5">{item.name}</AppText>
              <AppText className="text-sm text-gray-500 mb-2">{item.lastMessage}</AppText>
            </Container>
          </TouchableOpacity>
        )}
      />
    </Page>
  )
}
