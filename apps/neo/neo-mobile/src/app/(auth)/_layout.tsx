import { Slot, Stack } from 'expo-router';
import 'expo-dev-client';

export default function AuthLayout() {
  return (
    <Stack>
      <Stack.Screen name="login" options={{ headerShown: false }} />
    </Stack>
  );
}
