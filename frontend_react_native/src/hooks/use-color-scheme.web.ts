import { useEffect, useState } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';
import { useThemePreference } from '@/context/ThemeContext';

export function useColorScheme() {
  const [hasHydrated, setHasHydrated] = useState(false);

  useEffect(() => {
    setHasHydrated(true);
  }, []);

  try {
    const { colorScheme } = useThemePreference();
    if (hasHydrated) return colorScheme;
    return 'light';
  } catch {
    const rnScheme = useRNColorScheme();
    if (hasHydrated) return rnScheme === 'dark' ? 'dark' : 'light';
    return 'light';
  }
}
