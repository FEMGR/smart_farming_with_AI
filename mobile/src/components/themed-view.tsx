import { forwardRef } from 'react';
import { View, type ViewProps } from 'react-native';

import { ThemeColor } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export type ThemedViewProps = ViewProps & {
  lightColor?: string;
  darkColor?: string;
  type?: ThemeColor;
};

export const ThemedView = forwardRef<View, ThemedViewProps>(function ThemedView(
  { style, lightColor, darkColor, type, ...otherProps },
  ref
) {
  const theme = useTheme();

  return (
    <View
      ref={ref}
      style={[{ backgroundColor: theme[type ?? 'background'] }, style]}
      {...otherProps}
    />
  );
});
