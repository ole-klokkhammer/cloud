import { SafeAreaView, type ViewProps } from 'react-native';


export function Page(props: ViewProps) {
    const { className, ...otherProps } = props;

    return (
        <SafeAreaView className={`flex-1 bg-white dark:bg-zinc-900 ${className || ''}`} {...otherProps}>
            {props.children}
        </SafeAreaView>
    )
}
