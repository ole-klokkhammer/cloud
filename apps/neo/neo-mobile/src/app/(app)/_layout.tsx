import { ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { useColorScheme } from '@/common/hooks/theme/useColorScheme';
import { MyDarkTheme, MyLightTheme } from '@/common/constants/Theme';
import { ThemedView } from '@/common/components/view/ThemedView';
import { MqttClientProvider } from '@/common/context/mqtt/context';

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require('../../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return (
    <MqttClientProvider>
      <ThemeProvider value={colorScheme === 'dark' ? MyDarkTheme : MyLightTheme}>
        <ThemedView style={{ flex: 1 }}>
          <Stack>
            <Stack.Screen name="(app)/(tabs)" options={{ headerShown: false }} />
            <Stack.Screen name="(app)/chat/[id]" options={{ headerShown: true }} />
            <Stack.Screen name="(app)/+not-found" />
          </Stack>
          <StatusBar style="auto" />
        </ThemedView>
      </ThemeProvider>
    </MqttClientProvider>
  );
}
