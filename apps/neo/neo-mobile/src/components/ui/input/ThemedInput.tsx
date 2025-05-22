import React from 'react';
import { TextInput, TextInputProps, StyleSheet } from 'react-native';
import { useThemeColor } from '@/hooks/theme/useThemeColor';

export type ThemedInputProps = TextInputProps;

export function ThemedInput({
    style,
    ...rest
}: ThemedInputProps) {
    const backgroundColor = useThemeColor('inputBackground');
    const borderColor = useThemeColor('inputBorder');
    const color = useThemeColor('text');

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