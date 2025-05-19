import { useNavigation } from "expo-router";
import { styles } from "./login.screen.styles";
import { ThemedView } from "@/common/components/view/ThemedView";
import { Image } from 'react-native';
import { ThemedText } from "@/common/components/text/ThemedText";

export function LoginScreen() {
    const navigation = useNavigation();
    return (
        <ThemedView style={styles.container}>
            <Image src="/next.svg" style={styles.logo} />
            <ThemedText style={styles.title}>Login</ThemedText>

        </ThemedView>
    );
} 