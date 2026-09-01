import { useColorScheme as useRNColorScheme } from 'react-native';
import { useThemePreference } from '@/context/ThemeContext';

export function useColorScheme() {
  try {
    const { colorScheme } = useThemePreference();
    return colorScheme;
  } catch {
    const rnScheme = useRNColorScheme();
    return rnScheme === 'dark' ? 'dark' : 'light';
  }
}
