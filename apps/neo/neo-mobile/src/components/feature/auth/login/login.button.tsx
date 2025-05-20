import { useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { makeRedirectUri, useAuthRequest, useAutoDiscovery } from 'expo-auth-session';
import { Button } from 'react-native';
import { ThemedButton } from "@/components/ui/button/ThemedButton";
import { environment } from '@/constants/environment';
import React from 'react';


WebBrowser.maybeCompleteAuthSession();


export default function LoginButton() {
    // Endpoint
    const discovery = useAutoDiscovery('https://auth.linole.org/oauth2/default');
    // Request
    const [request, response, promptAsync] = useAuthRequest(
        {
            clientId: environment.keycloak.clientId,
            scopes: ['openid', 'profile'],
            redirectUri: makeRedirectUri({
                native: 'com.okta.auth.linole.org:/callback',
            }),
        },
        discovery
    );

    useEffect(() => {
        if (response?.type === 'success') {
            const { code } = response.params;
        }
    }, [response]);


    <ThemedButton disabled={!request}
    title="Login"
    onPress={() => {
        promptAsync();
    }} />
    return (
        <Button
            disabled={!request}
            title="Login"
            onPress={() => {
                promptAsync();
            }}
        />
    );
}
