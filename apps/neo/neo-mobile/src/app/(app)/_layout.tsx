import { ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { useColorScheme } from '@/hooks/theme/useColorScheme';
import { MyDarkTheme, MyLightTheme } from '@/constants/Theme';
import { ThemedView } from '@/components/ui/view/ThemedView';
import { MqttClientProvider } from '@/context/mqtt/context';
import { useAuth } from '@/context/auth/context';
import { router } from "expo-router";

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const { initializing, authenticated } = useAuth();
  const colorScheme = useColorScheme();
  const [loaded] = useFonts({
    SpaceMono: require('../../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  useEffect(() => {
    if (!initializing) {
      if (!authenticated) {
        console.log('not authenticated, redirecting to login');
        router.replace('/login');
      }
    }
  }, [initializing, authenticated]);

  if (!loaded) {
    return null;
  } else {
    return (
      <>
        <MqttClientProvider>
          <ThemeProvider value={colorScheme === 'dark' ? MyDarkTheme : MyLightTheme}>
            <ThemedView style={{ flex: 1 }}>
              <Stack>
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="chat/[id]" options={{ headerShown: true }} />
                <Stack.Screen name="+not-found" />
              </Stack>
              <StatusBar style="dark" />
            </ThemedView>
          </ThemeProvider>
        </MqttClientProvider>
      </>
    );
  }
}
