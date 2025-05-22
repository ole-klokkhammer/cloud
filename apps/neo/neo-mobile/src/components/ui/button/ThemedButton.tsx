import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle, TextStyle, GestureResponderEvent } from 'react-native';
import { useThemeColor } from '@/hooks/theme/useThemeColor';

type ThemedButtonProps = {
    title: string;
    onPress: (event: GestureResponderEvent) => void;
    style?: ViewStyle;
    textStyle?: TextStyle;
    disabled?: boolean;
};

export function ThemedButton(
    {
        title,
        onPress,
        style,
        textStyle,
        disabled,
    }: ThemedButtonProps) {
    const backgroundColor = useThemeColor('button');
    const color = useThemeColor('buttonText');
    const disabledBg = useThemeColor('buttonDisabled');

    return (
        <TouchableOpacity
            style={[
                styles.button,
                { backgroundColor: disabled ? disabledBg : backgroundColor },
                style,
            ]}
            onPress={onPress}
            activeOpacity={0.8}
            disabled={disabled}
        >
            <Text style={[styles.buttonText, { color }, textStyle]}>{title}</Text>
        </TouchableOpacity>
    );
}

const styles = StyleSheet.create({
    button: {
        paddingVertical: 10,
        paddingHorizontal: 22,
        borderRadius: 20,
        alignItems: 'center',
        justifyContent: 'center',
        minWidth: 64,
    },
    buttonText: {
        fontSize: 16,
        fontWeight: '600',
    },
});