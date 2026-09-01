import React, { createContext, useContext, useEffect, useState } from 'react';
import { useColorScheme as useRNColorScheme } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { colorConfig, getThemeColors, ThemeColors } from '@/constants/color_config';

export type ThemePreference = 'system' | 'light' | 'dark';

interface ThemeContextType {
  themePreference: ThemePreference;
  setThemePreference: (preference: ThemePreference) => void;
  colorScheme: 'light' | 'dark';
  colors: ThemeColors;
  isDark: boolean;
}

const THEME_STORAGE_KEY = '@app_theme_preference';

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemePreferenceProvider({ children }: { children: React.ReactNode }) {
  const systemScheme = useRNColorScheme();
  const [themePreference, setThemePreferenceState] = useState<ThemePreference>('system');
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    async function loadThemePreference() {
      try {
        const savedPref = await AsyncStorage.getItem(THEME_STORAGE_KEY);
        if (savedPref === 'light' || savedPref === 'dark' || savedPref === 'system') {
          setThemePreferenceState(savedPref as ThemePreference);
        }
      } catch (e) {
        console.error('Failed to load theme preference', e);
      } finally {
        setIsLoaded(true);
      }
    }
    loadThemePreference();
  }, []);

  const setThemePreference = async (preference: ThemePreference) => {
    setThemePreferenceState(preference);
    try {
      await AsyncStorage.setItem(THEME_STORAGE_KEY, preference);
    } catch (e) {
      console.error('Failed to save theme preference', e);
    }
  };

  const resolvedScheme: 'light' | 'dark' =
    themePreference === 'system'
      ? systemScheme === 'dark'
        ? 'dark'
        : 'light'
      : themePreference;

  const colors = getThemeColors(resolvedScheme);
  const isDark = resolvedScheme === 'dark';

  return (
    <ThemeContext.Provider
      value={{
        themePreference,
        setThemePreference,
        colorScheme: resolvedScheme,
        colors,
        isDark,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useThemePreference() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemePreference must be used within a ThemePreferenceProvider');
  }
  return context;
}
