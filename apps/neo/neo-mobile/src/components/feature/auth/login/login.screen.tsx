import React from "react";
import { styles } from "./login.screen.styles";
import { ThemedView } from "@/components/ui/view/ThemedView";
import { ThemedText } from "@/components/ui/text/ThemedText";
import LoginButton from "./login.button";

export function LoginScreen() {

    return (
        <ThemedView style={styles.container}>
            <ThemedText style={styles.title}>Login</ThemedText>
            <LoginButton />
        </ThemedView>
    );
}