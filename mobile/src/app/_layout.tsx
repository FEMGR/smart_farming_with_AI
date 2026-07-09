import React from 'react';
import { ActivityIndicator, useColorScheme } from 'react-native';
import { DarkTheme, DefaultTheme, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';

import { AnimatedSplashOverlay } from '@/components/animated-icon';
import AppTabs from '@/components/app-tabs';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { DataProvider } from '@/context/DataContext';
import { AuthScreen } from '@/components/auth-screen';

SplashScreen.preventAutoHideAsync();

function MainAppShell() {
  const { token, loading } = useAuth();
  const colorScheme = useColorScheme();

  if (loading) {
    return (
      <ActivityIndicator
        size="large"
        color="#10B981"
        style={{ flex: 1, justifyContent: 'center', backgroundColor: colorScheme === 'dark' ? '#000' : '#fff' }}
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
    <AuthProvider>
      <DataProvider>
        <MainAppShell />
      </DataProvider>
    </AuthProvider>
  );
}
