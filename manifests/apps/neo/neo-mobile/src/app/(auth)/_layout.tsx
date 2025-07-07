import { router, Stack } from 'expo-router';
import 'expo-dev-client';
import { useEffect } from 'react';
import { useAuth } from '@/context/auth/context';

export default function AuthLayout() {
  const { initializing, authenticated } = useAuth();

  useEffect(() => {
    if (!initializing) {
      if (authenticated) {
        console.log('already authenticated, redirecting to main screen');
        router.replace('/');
      }
    }
  }, [initializing, authenticated]);

  return (
    <Stack>
      <Stack.Screen name="login" options={{ headerShown: false }} />
    </Stack>
  );
}
