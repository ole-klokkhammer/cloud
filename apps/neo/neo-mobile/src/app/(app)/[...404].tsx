import { Link } from 'expo-router';
import { AppText } from '@/components/ui/text/text';
import { Page } from '@/components/ui/layout/page';

export default function NotFound() {
  return (
    <Page className="flex-1 items-center justify-center p-20">
      <AppText type="title">This screen doesn't exist.</AppText>
      <Link href="/home" className='mt-15 p-15'>
        <AppText type="link">Go to home screen!</AppText>
      </Link>
    </Page>
  );
} 
