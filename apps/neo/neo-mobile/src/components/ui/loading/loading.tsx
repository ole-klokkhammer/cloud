import React from 'react';
import { ActivityIndicator } from 'react-native';
import { styles } from './loading.styling';
import { Container } from '@/components/ui/layout/container';

const AppLoading = () => {
    return (
        <Container style={styles.container}>
            <ActivityIndicator size="large" color="#0000ff" />
        </Container>
    );
};

export default AppLoading;