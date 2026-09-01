/**
 * Hook for accessing centralized color configuration and active theme.
 */

import { Colors, palette, colorConfig, ThemeColors, ThemeMode } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';

export function useTheme(): ThemeColors {
  const scheme = useColorScheme();
  const theme: ThemeMode = scheme === 'dark' ? 'dark' : 'light';

  return Colors[theme];
}

export const useThemeColors = useTheme;

export function useColorConfig() {
  const scheme = useColorScheme();
  const mode: ThemeMode = scheme === 'dark' ? 'dark' : 'light';

  return {
    colors: Colors[mode],
    palette,
    colorConfig,
    scheme,
    mode,
    isDark: mode === 'dark',
  };
}
