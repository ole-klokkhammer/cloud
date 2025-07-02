// Example React Native component using NativeWind
import { View, Text } from "react-native";

type CardProps = {
    className?: string;
    header: string;
    children?: React.ReactNode;
};

export function Card(props: CardProps) {
    return (
        <View className={`bg-white dark:bg-gray-800 rounded-lg p-6 ring shadow-xl ring-gray-900/5 ${props.className}`}>
            <Text className="text-gray-900 dark:text-white mt-5 text-base  ">
                {props.header}
            </Text>
            <View className="mt-2">
                {props.children}
            </View>
        </View>
    );
}