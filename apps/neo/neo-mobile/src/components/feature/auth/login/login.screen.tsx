import React from "react";
import { styles } from "./login.screen.styles";
import { ThemedView } from "@/components/ui/view/ThemedView";
import { ThemedText } from "@/components/ui/text/ThemedText";
import * as WebBrowser from 'expo-web-browser';
import { ThemedButton } from "@/components/ui/button/ThemedButton";
import { handleLogin } from "@/services/auth/authentication";

WebBrowser.maybeCompleteAuthSession();

export function LoginScreen() {

    return (
        <ThemedView style={styles.container}>
            <ThemedText style={styles.title}>Login</ThemedText>
            <ThemedButton
                title="Login"
                onPress={handleLogin}
            />
        </ThemedView>
    );
}