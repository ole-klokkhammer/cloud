import React, { useState } from "react";
import { useNavigation } from "expo-router";
import { styles } from "./login.screen.styles";
import { ThemedView } from "@/components/ui/view/ThemedView";
import { ThemedText } from "@/components/ui/text/ThemedText";
import { TextInput, Button, Alert } from "react-native";
import { ThemedInput } from "@/components/ui/input/ThemedInput";

export function LoginScreen() {
    const navigation = useNavigation();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleLogin = async () => {
        setLoading(true);

        setLoading(false);
    };

    return (
        <ThemedView style={styles.container}>
            <ThemedText style={styles.title}>Login</ThemedText>
            <ThemedInput
                style={styles.input}
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
            />
            <ThemedInput
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
            />
            <Button title={loading ? "Logging in..." : "Login"} onPress={handleLogin} disabled={loading} />
        </ThemedView>
    );
}