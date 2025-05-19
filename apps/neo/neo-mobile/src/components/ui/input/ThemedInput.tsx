import React from 'react';
import { TextInput, TextInputProps, StyleSheet } from 'react-native';
import { useThemeColor } from '@/hooks/theme/useThemeColor';

export type ThemedInputProps = TextInputProps & {
    lightBackgroundColor?: string;
    darkBackgroundColor?: string;
    lightBorderColor?: string;
    darkBorderColor?: string;
    lightTextColor?: string;
    darkTextColor?: string;
};

export function ThemedInput({
    style,
    lightBackgroundColor,
    darkBackgroundColor,
    lightBorderColor,
    darkBorderColor,
    lightTextColor,
    darkTextColor,
    ...rest
}: ThemedInputProps) {
    const backgroundColor = useThemeColor({ light: lightBackgroundColor, dark: darkBackgroundColor }, 'inputBackground');
    const borderColor = useThemeColor({ light: lightBorderColor, dark: darkBorderColor }, 'inputBorder');
    const color = useThemeColor({ light: lightTextColor, dark: darkTextColor }, 'text');

    return (
        <TextInput
            style={[
                styles.input,
                { backgroundColor, borderColor, color },
                style,
            ]}
            placeholderTextColor={color}
            {...rest}
        />
    );
}

const styles = StyleSheet.create({
    input: {
        flex: 1,
        borderWidth: 1,
        borderRadius: 20,
        paddingHorizontal: 14,
        paddingVertical: 8,
        marginRight: 8,
        fontSize: 16,
    },
});