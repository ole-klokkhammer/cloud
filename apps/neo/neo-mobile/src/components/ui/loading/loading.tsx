import React from 'react';
import { ActivityIndicator } from 'react-native';
import { styles } from './loading.styling';
import { AppContainer } from '@/components/ui/container/container';

const AppLoading = () => {
    return (
        <AppContainer style={styles.container}>
            <ActivityIndicator size="large" color="#0000ff" />
        </AppContainer>
    );
};

export default AppLoading;