import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ViewStyle, TextStyle, GestureResponderEvent } from 'react-native';
import { useThemeColor } from '@/common/hooks/theme/useThemeColor';

type ThemedButtonProps = {
    title: string;
    onPress: (event: GestureResponderEvent) => void;
    style?: ViewStyle;
    textStyle?: TextStyle;
    disabled?: boolean;
    lightColor?: string;
    darkColor?: string;
    lightDisabledColor?: string;
    darkDisabledColor?: string;
    lightBgColor?: string;
    darkBgColor?: string;
};

export function ThemedButton(
    {
        title,
        onPress,
        style,
        textStyle,
        disabled,
        lightColor,
        darkColor,
        lightBgColor,
        darkBgColor,
        lightDisabledColor,
        darkDisabledColor,
    }: ThemedButtonProps) {
    const backgroundColor = useThemeColor({ light: lightBgColor, dark: darkBgColor }, 'button');
    const color = useThemeColor({ light: lightColor, dark: darkColor }, 'buttonText');
    const disabledBg = useThemeColor({ light: lightDisabledColor, dark: darkDisabledColor }, 'buttonDisabled');

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