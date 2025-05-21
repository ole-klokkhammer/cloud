import * as SecureStore from 'expo-secure-store';

export enum TokenKey {
    AccessToken = 'access_token',
    RefreshToken = 'refresh_token',
    IdToken = 'id_token',
    ExpiresIn = 'expires_in',
}

export async function getToken(key: TokenKey) {
    return await SecureStore.getItemAsync(key);
}

export async function deleteToken(key: TokenKey) {
    await SecureStore.deleteItemAsync(key);
}

export async function isTokenExpired() {
    const expiryTime = await SecureStore.getItemAsync(TokenKey.ExpiresIn);
    return Date.now() > Number(expiryTime);
}

export async function saveToken(key: TokenKey, value: string) {
    await SecureStore.setItemAsync(key, value, {
        keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
    });
}