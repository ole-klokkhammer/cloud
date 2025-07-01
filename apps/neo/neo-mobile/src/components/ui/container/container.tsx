import { View, type ViewProps } from 'react-native';

import { useThemeColor } from '@/hooks/theme/useThemeColor';

export type ThemedViewProps = ViewProps & {
  lightColor?: string;
  darkColor?: string;
};

export function AppContainer({ style, lightColor, darkColor, ...otherProps }: ThemedViewProps) {
  const backgroundColor = useThemeColor('background');

  return <View style={[{ backgroundColor }, style]} {...otherProps} />;
}
