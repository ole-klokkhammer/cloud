import { ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import 'react-native-reanimated';
import { useColorScheme } from '@/hooks/theme/useColorScheme';
import { MyDarkTheme, MyLightTheme } from '@/constants/Theme';
import { AppContainer } from '@/components/ui/container/container';
import { MqttClientProvider } from '@/context/mqtt/context';
import { useAuth } from '@/context/auth/context';
import { router } from "expo-router";
import { Drawer } from 'expo-router/drawer';
import { Platform, useWindowDimensions } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

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
      <>
        <MqttClientProvider>
          <ThemeProvider value={colorScheme === 'dark' ? MyDarkTheme : MyLightTheme}>
            <AppContainer style={{ flex: 1 }}>
              <GestureHandlerRootView style={{ flex: 1 }}>
                <Drawer
                  initialRouteName="index"
                  screenOptions={{
                    drawerType: Platform.OS === 'web' && window.width >= 900 ? 'permanent' : 'front',
                    headerShown: true,
                  }}
                >
                  <Drawer.Screen
                    name="index"
                    options={{
                      drawerLabel: "Home",
                      title: "Home",
                    }}
                  />
                  <Drawer.Screen
                    key={'kubernetes'}
                    name="monitoring"
                    options={{
                      headerShown: true,
                      drawerLabel: "Monitoring",
                      title: "Monitoring",
                    }}
                  /> 
                  <Drawer.Screen
                    name="account"
                    options={{
                      drawerLabel: "Account",
                      title: "Account",
                    }}
                  />
                  <Drawer.Screen
                    name="surveillance"
                    options={{
                      drawerLabel: "Surveillance",
                      title: "Surveillance",
                    }}
                  />
                  <Drawer.Screen
                    name="[...404]"
                    options={{
                      drawerItemStyle: { display: 'none' },
                    }}
                  />
                </Drawer>
              </GestureHandlerRootView>
            </AppContainer>
          </ThemeProvider>
        </MqttClientProvider>
      </>
    );
  }
}
