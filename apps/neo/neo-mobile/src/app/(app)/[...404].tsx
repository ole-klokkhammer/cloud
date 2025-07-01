import { Link, Stack } from 'expo-router';
import { StyleSheet } from 'react-native';

import { AppText } from '@/components/ui/text/text';
import { AppContainer } from '@/components/ui/container/container';

export default function NotFound() {
  return (
    <>
      <Stack.Screen options={{ title: 'Oops!' }} />
      <AppContainer style={styles.container}>
        <AppText type="title">This screen doesn't exist.</AppText>
        <Link href="/home" style={styles.link}>
          <AppText type="link">Go to home screen!</AppText>
        </Link>
      </AppContainer>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  link: {
    marginTop: 15,
    paddingVertical: 15,
  },
});
