import React, { useEffect, useRef } from 'react';
import { Animated, Dimensions, StyleSheet, Text, View } from 'react-native';
import { ThemedView } from '../view/ThemedView';

const { width, height } = Dimensions.get('window');
const COLUMN_WIDTH = 20;
const FONT_SIZE = 16;
const COLUMNS = Math.floor(width / COLUMN_WIDTH);
const CHAR_SET = '01';

function randomChar() {
    return CHAR_SET[Math.floor(Math.random() * CHAR_SET.length)];
}

function MatrixColumn({ height, speed }: { height: number; speed: number }) {
    const animatedValue = useRef(new Animated.Value(0)).current;
    const [chars, setChars] = React.useState<string[]>([]);

    useEffect(() => {
        setChars(Array.from({ length: Math.ceil(height / FONT_SIZE) }, randomChar));

        const animate = () => {
            animatedValue.setValue(-FONT_SIZE * chars.length);
            Animated.timing(animatedValue, {
                toValue: height,
                duration: speed,
                useNativeDriver: true,
            }).start(() => {
                setChars(Array.from({ length: Math.ceil(height / FONT_SIZE) }, randomChar));
                animate();
            });
        };
        animate();
    }, []);

    return (
        <Animated.View style={{ transform: [{ translateY: animatedValue }] }}>
            {chars.map((char, i) => (
                <Text key={i} style={styles.char}>
                    {char}
                </Text>
            ))}
        </Animated.View>
    );
}

export default function MatrixBackground() {
    return (
        <ThemedView style={styles.container}>
            <ThemedView style={styles.background}>
                {Array.from({ length: COLUMNS }).map((_, i) => (
                    <ThemedView key={i} style={{ width: COLUMN_WIDTH, overflow: 'hidden' }}>
                        <MatrixColumn
                            height={height}
                            speed={4000 + Math.random() * 3000}
                        />
                    </ThemedView>
                ))}
            </ThemedView>
        </ThemedView>
    );
}

const styles = StyleSheet.create({
    container: {
        width: '100%',
        height: 250,
    },
    background: {
        backgroundColor: '#000',
        width: '100%',
        height: '100%',
        flexDirection: 'row',
        position: 'absolute',
        left: 0,
        top: 0,
    },
    char: {
        color: '#00ff41',
        fontSize: FONT_SIZE,
        fontFamily: 'monospace',
        textAlign: 'center',
        textShadowColor: '#0f0',
        textShadowOffset: { width: 0, height: 0 },
        textShadowRadius: 6,
    },
});