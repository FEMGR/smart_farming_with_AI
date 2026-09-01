import React from 'react';
import { ActivityIndicator } from 'react-native';
import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';

import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { DataProvider } from '@/context/DataContext';
import { ThemePreferenceProvider, useThemePreference } from '@/context/ThemeContext';
import { AuthScreen } from '@/components/auth-screen';

SplashScreen.preventAutoHideAsync();

function MainAppShell() {
  const { token, loading } = useAuth();
  const { colorScheme, colors } = useThemePreference();

  if (loading) {
    return (
      <ActivityIndicator
        size="large"
        color={colors.primary}
        style={{ flex: 1, justifyContent: 'center', backgroundColor: colors.background }}
      />
    );
  }

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <AnimatedSplashOverlay />
      {!token ? <AuthScreen /> : <AppTabs />}
    </ThemeProvider>
  );
}

export default function RootLayout() {
  return (
    <ThemePreferenceProvider>
      <AuthProvider>
        <DataProvider>
          <MainAppShell />
        </DataProvider>
      </AuthProvider>
    </ThemePreferenceProvider>
  );
}
