import { ActivityIndicator, SafeAreaView, type ViewProps } from 'react-native';

export function LoadingPage(props: ViewProps) {
    const { className, ...otherProps } = props;

    return (
        <SafeAreaView className={`bg-white dark:bg-black ${className || ''}`} {...otherProps}>
            <ActivityIndicator className='flex-1 justify-center align-middle' size="large" color="#0000ff" />
        </SafeAreaView>
    )
}
