import React, { useEffect } from 'react';
import * as WebBrowser from 'expo-web-browser';
import { makeRedirectUri, useAuthRequest, useAutoDiscovery } from 'expo-auth-session';
import { Button } from 'react-native';
import { environment } from '@/constants/environment';

WebBrowser.maybeCompleteAuthSession();

export default function LoginButton() {
    const discovery = useAutoDiscovery(environment.keycloak.issuer);
 
    const [request, response, promptAsync] = useAuthRequest(
        {
            clientId: environment.keycloak.clientId,
            scopes: environment.keycloak.scopes,
            redirectUri: makeRedirectUri({
                scheme: environment.keycloak.redirectUrl,
            }),
        },
        discovery
    );

    // Handle the authentication response
    useEffect(() => {
        if (response?.type === 'success') {
            const { code } = response.params;
            console.log('Authorization code:', code);
        }
    }, [response]);

    return (
        <Button
            disabled={!request}
            title="Login"
            onPress={() => {
                console.log('Request:', request);
                promptAsync();
            }}
        />
    );
}