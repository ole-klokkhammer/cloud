import React from 'react';
import { ActivityIndicator } from 'react-native';
import { styles } from './Loading.styling';
import { ThemedView } from '../view/ThemedView';

const Loading = () => {
    return (
        <ThemedView style={styles.container}>
            <ActivityIndicator size="large" color="#0000ff" />
        </ThemedView>
    );
};

export default Loading;