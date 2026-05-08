import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export enum TokenKey {
    AccessToken = 'access_token',
    RefreshToken = 'refresh_token',
    IdToken = 'id_token',
    ExpiryTime = 'expiry_time',
}

export async function getItem(key: TokenKey): Promise<string | null> {
    if (Platform.OS === 'web') {
        return await AsyncStorage.getItem(key);
    } else {
        return await SecureStore.getItemAsync(key);
    }
}

export async function deleteItem(key: TokenKey): Promise<void> {
    if (Platform.OS === 'web') {
        await AsyncStorage.removeItem(key);
    } else {
        await SecureStore.deleteItemAsync(key);
    }
}

export async function saveItem(key: TokenKey, value: string): Promise<void> {
    if (Platform.OS === 'web') {
        await AsyncStorage.setItem(key, value);
    } else {
        await SecureStore.setItemAsync(key, value, {
            keychainAccessible: SecureStore.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
        });
    }
}

export async function isTokenExpired(): Promise<boolean> {
    if (Platform.OS === 'web') {
        const expiryTime = await getItem(TokenKey.ExpiryTime);
        return Date.now() > Number(expiryTime);
    } else {
        const expiryTime = await SecureStore.getItemAsync(TokenKey.ExpiryTime);
        return Date.now() > Number(expiryTime);
    }
}