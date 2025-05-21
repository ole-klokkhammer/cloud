import React from 'react';
import * as WebBrowser from 'expo-web-browser';
import { CodeChallengeMethod, makeRedirectUri } from 'expo-auth-session';
import { Button, Linking } from 'react-native';
import { environment } from '@/constants/environment';

WebBrowser.maybeCompleteAuthSession();

export default function LoginButton() {

    const handleToken = async (code: string, code_verifier: string) => {
        const response = await fetch(environment.keycloak.tokenEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code,
                code_verifier,
                redirect_uri: makeRedirectUri({
                    scheme: environment.keycloak.redirectUrl,
                }),
            }),
        });

        const data = await response.json();
        console.log('Token response:', data);
    }

    const onLogin = async () => {
        const codeVerifier = generateCodeVerifier();
        const codeChallenge = await generateCodeChallenge(codeVerifier);

        let url = environment.keycloak.authorizeEndpoint;
        url += '?redirect_uri=' + encodeURIComponent(makeRedirectUri({
            scheme: environment.keycloak.redirectUrl,
        }));
        url += '&code_challenge=' + encodeURIComponent(codeChallenge);
        url += '&code_challenge_method=' + encodeURIComponent(CodeChallengeMethod.S256);

        const result = await WebBrowser.openAuthSessionAsync(url);
        if (result.type === 'success') {
            const params = new URLSearchParams(result.url.split('?')[1]);
            const code = params.get('code');
            handleToken(code!, codeVerifier!);
        }
    }

    function generateCodeVerifier() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return btoa(String.fromCharCode(...array))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }

    async function generateCodeChallenge(codeVerifier: string) {
        const encoder = new TextEncoder();
        const data = encoder.encode(codeVerifier);
        const digest = await crypto.subtle.digest('SHA-256', data);
        return btoa(String.fromCharCode(...new Uint8Array(digest)))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=+$/, '');
    }

    return (
        <Button
            title="Login"
            onPress={onLogin}
        />
    );
}