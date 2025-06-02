import { environment } from "@/constants/environment";
import { CodeChallengeMethod, makeRedirectUri } from "expo-auth-session";
import * as WebBrowser from 'expo-web-browser';
import { saveItem, TokenKey } from "./token";
import * as jwt from 'jwt-decode'
import CryptoJS from "crypto-js";

export const handleLogin = async () => {
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);

    let url = environment.keycloak.authorizeEndpoint;
    url += '?redirect_uri=' + encodeURIComponent(makeRedirectUri({
        scheme: environment.keycloak.scheme,
    }));
    url += '&code_challenge=' + encodeURIComponent(codeChallenge);
    url += '&code_challenge_method=' + encodeURIComponent(CodeChallengeMethod.S256);

    const result = await WebBrowser.openAuthSessionAsync(url);
    if (result.type === 'success') {
        const params = new URLSearchParams(result.url.split('?')[1]);
        const code = params.get('code');

        // FIXME, if we dont await here, the app might not redirect to the right page after login
        await handleToken(code!, codeVerifier!);
    } else {
        console.error('Login failed:', result);
    }
}

export const handleLogout = async () => {
    console.error('Logout not implemented');
}

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
                scheme: environment.keycloak.scheme,
            }),
        }),
    });

    const data = await response.json();

    // FIXME, if we dont await here, the app might not redirect to the right page after login
    await saveItem(TokenKey.AccessToken, data.access_token);
    await saveItem(TokenKey.RefreshToken, data.refresh_token);
    await saveItem(TokenKey.IdToken, data.id_token);

    const parsedToken = jwt.jwtDecode(data.access_token);
    await saveItem(TokenKey.ExpiryTime, String(Number(parsedToken.exp) * 1000));
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
    const hash = CryptoJS.SHA256(codeVerifier);
    const base64Hash = CryptoJS.enc.Base64.stringify(hash)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

    return base64Hash;
}