import React from "react";
import { styles } from "./login.screen.styles";
import { AppContainer } from "@/components/ui/container/container";
import { AppText } from "@/components/ui/text/text";
import * as WebBrowser from 'expo-web-browser';
import { AppButton } from "@/components/ui/button/button"; 
import { useAuth } from "@/context/auth/context";

WebBrowser.maybeCompleteAuthSession();

export function LoginScreen() {
    const { login } = useAuth();
    return (
        <AppContainer style={styles.container}>
            <AppText style={styles.title}>Login</AppText>
            <AppButton
                title="Login"
                onPress={login}
            />
        </AppContainer>
    );
}