import { Link } from 'expo-router';
import { Page } from '@/components/ui/page/Page';
import { LinkText } from '@/components/ui/link';
import { Heading } from '@/components/ui/heading';

export default function NotFound() {
  return (
    <Page className="flex-1 items-center justify-center p-20">
      <Heading bold >This screen doesn't exist.</Heading>
      <Link href="/home" className='mt-15 p-15'>
        <LinkText>Go to home screen!</LinkText>
      </Link>
    </Page>
  );
} 
