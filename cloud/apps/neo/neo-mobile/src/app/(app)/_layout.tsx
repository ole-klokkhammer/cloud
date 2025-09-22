import { ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { useColorScheme } from '@/hooks/theme/useColorScheme';
import { MyDarkTheme, MyLightTheme } from '@/constants/Theme';
import { MqttClientProvider } from '@/context/mqtt/context';
import { useAuth } from '@/context/auth/context';
import { router, Stack, Tabs } from "expo-router";
import { Drawer } from 'expo-router/drawer';
import { Platform, useWindowDimensions } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Box } from '@/components/ui/layout/Box';

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const window = useWindowDimensions();
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
      <MqttClientProvider>
        <ThemeProvider value={colorScheme === 'dark' ? MyDarkTheme : MyLightTheme}>
          <GestureHandlerRootView className='flex-1'>
            <Stack>
              <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
            </Stack>
          </GestureHandlerRootView>
        </ThemeProvider>
      </MqttClientProvider>
    );
  }
}
