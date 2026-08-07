/**
 * Centralized Color Management Configuration for Mobile React Native App
 * Forest Edition (Soft & Premium)
 * 
 * This file serves as the single source of truth for all colors in the application,
 * incorporating base tokens, light & dark mode semantic mappings, status colors,
 * domain-specific action colors, and helper functions.
 */

import { ColorSchemeName } from 'react-native';

// -----------------------------------------------------------------------------
// 1. BASE COLOR PALETTE (TOKENS) - FOREST EDITION
// -----------------------------------------------------------------------------
export const forestGreen = {
  50: '#EAF2EC',
  100: '#CBDECE',
  200: '#B8C6BE',
  300: '#A0C4A5',
  400: '#7AAE83',
  500: '#4F7C59', // Core Primary
  600: '#3F6847',
  700: '#33553A',
  800: '#26422D',
  900: '#1E2F21',
} as const;

export const mossGreen = {
  50: '#F0F3ED',
  100: '#DCE5D6',
  200: '#C5D5C2',
  300: '#98B896',
  400: '#6FB872', // Core Secondary
  500: '#65B072',
  600: '#5B7A5E',
  700: '#354A3A',
  800: '#2A362C',
  900: '#1D261E',
} as const;

export const sage = {
  50: '#F2F4F1',
  100: '#E2E7E1',
  200: '#CCD7CD',
  300: '#B6C6B7',
  400: '#A8C9B0',
  500: '#7FA18A', // Core Accent
  600: '#65826E',
  700: '#4D6354',
  800: '#35443A',
  900: '#2F3C33',
} as const;

export const soilBrown = {
  50: '#FBF8F4',
  100: '#F1ECE6',
  200: '#E4D7C9',
  300: '#D7C2AF',
  400: '#C9A893',
  500: '#A47F63',
  600: '#8C644F',
  700: '#6C4B3F',
  800: '#5B3A2C',
  900: '#3E261F',
} as const;

export const amber = {
  50: '#FFFAEB',
  100: '#FEF3C7',
  200: '#FDE6B3',
  300: '#FAD67A',
  400: '#F7C359',
  500: '#E0A534', // Core Warning
  600: '#A37F16',
  700: '#7F5812',
  800: '#634710',
  900: '#5D3E0D',
} as const;

export const terracotta = {
  50: '#FFF2F0',
  100: '#FCDAD6',
  200: '#F0B4A0',
  300: '#F08B81',
  400: '#E56363',
  500: '#D54B44', // Core Error
  600: '#954944',
  700: '#893337',
  800: '#752726',
  900: '#5A1C19',
} as const;

export const stoneGray = {
  50: '#FAFBF8',
  100: '#F1F3F1',
  200: '#E3E7E3',
  300: '#CCD2CF',
  400: '#A6B0AF',
  500: '#8A938F',
  600: '#60746F',
  700: '#47524B',
  800: '#2A332E',
  900: '#1F2A22',
} as const;

export const common = {
  white: '#FFFFFF',
  black: '#0D0D0D',
  transparent: 'transparent',
  overlay: 'rgba(0, 0, 0, 0.45)',
  lightOverlay: 'rgba(0, 0, 0, 0.12)',
} as const;

export const palette = {
  forestGreen,
  mossGreen,
  sage,
  soilBrown,
  amber,
  terracotta,
  stoneGray,
  common,

  // Compatibility Aliases
  emerald: forestGreen,
  blue: mossGreen,
  cyan: sage,
  purple: { 50: '#F5F3FF', 100: '#EDE9FE', 500: '#8E7CC3', 600: '#371c65', 700: '#6D28D9' },
  red: terracotta,
  gray: stoneGray,
} as const;


// -----------------------------------------------------------------------------
// 2. SEMANTIC COLOR INTERFACE & CONFIGURATION
// -----------------------------------------------------------------------------
export interface ThemeColors {
  // Surfaces & Backgrounds
  background: string;
  backgroundElement: string;
  backgroundSelected: string;
  surface: string;
  surfaceSubtle: string;
  card: string;
  modal: string;
  border: string;

  // Text Colors
  text: string;
  textSecondary: string;
  textTertiary: string;
  textMuted: string;
  textInverse: string;

  // Brand Colors
  primary: string;
  secondary: string;
  accent: string;
  primaryLight: string;
  primaryDark: string;
  tint: string;

  // Status Colors
  success: string;
  successBackground: string;
  successText: string;
  warning: string;
  warningBackground: string;
  warningText: string;
  error: string;
  errorBackground: string;
  errorText: string;
  info: string;
  infoBackground: string;
  infoText: string;

  // Interactive & Controls
  borderFocus: string;
  divider: string;
  inputBackground: string;
  inputBorder: string;
  placeholder: string;
  disabled: string;
  disabledText: string;

  // Navigation & Tab Bar
  tabBarBackground: string;
  tabBarActive: string;
  tabBarInactive: string;
  tabBarBorder: string;

  // Domain Specific (Smart Farming Care Actions)
  careWater: string;
  careFertilize: string;
  carePrune: string;
  careHarvest: string;
}

export const lightTheme: ThemeColors = {
  // Surfaces & Backgrounds
  background: '#d6dace',
  backgroundElement: '#F5F7F4',
  backgroundSelected: '#E2E7E1',
  surface: '#FFFFFF',
  surfaceSubtle: '#F5F7F4',
  card: '#E2F7E3',
  modal: '#FFFFFF',
  border: '#E2E7E1',

  // Text Colors
  text: '#1F2A22',
  textSecondary: '#47524B',
  textTertiary: '#6B756F',
  textMuted: '#8C958F',
  textInverse: '#FFFFFF',

  // Brand Colors
  primary: '#4F7C59',
  secondary: '#6FB872',
  accent: '#7FA18A',
  primaryLight: '#E6FEE8',
  primaryDark: '#33553A',
  tint: '#4F7C59',

  // Status Colors
  success: '#4F7C59',
  successBackground: '#EAF2EC',
  successText: '#33553A',
  warning: '#E0A534',
  warningBackground: '#FFFAEB',
  warningText: '#7F5812',
  error: '#70120d',
  errorBackground: '#FFF2F0',
  errorText: '#893337',
  info: '#4A90A6',
  infoBackground: '#F2F4F1',
  infoText: '#35443A',

  // Interactive & Controls
  borderFocus: '#4F7C59',
  divider: '#E2E7E1',
  inputBackground: '#FFFFFF',
  inputBorder: '#CCD2CF',
  placeholder: '#8C958F',
  disabled: '#E3E7E3',
  disabledText: '#A6B0AF',

  // Navigation & Tab Bar
  tabBarBackground: '#FFFFFF',
  tabBarActive: '#4F7C59',
  tabBarInactive: '#8C958F',
  tabBarBorder: '#E2E7E1',

  // Domain Specific (Care Actions)
  careWater: '#5FA79A',
  careFertilize: '#7FA18A',
  carePrune: '#8E7CC3',
  careHarvest: '#6FB872',
};

export const darkTheme: ThemeColors = {
  // Surfaces & Backgrounds
  background: '#0E1411',
  backgroundElement: '#1F2621',
  backgroundSelected: '#2A332E',
  surface: '#161C18',
  surfaceSubtle: '#1F2621',
  card: '#1A211D',
  modal: '#161C18',
  border: '#2A332E',

  // Text Colors
  text: '#E6EEE7',
  textSecondary: '#B0BBB4',
  textTertiary: '#8A958F',
  textMuted: '#6D776F',
  textInverse: '#0E1411',

  // Brand Colors
  primary: '#81B28A',
  secondary: '#9BB896',
  accent: '#A8C9B0',
  primaryLight: 'rgba(127, 162, 138, 0.15)',
  primaryDark: '#4F7C59',
  tint: '#81B28A',

  // Status Colors
  success: '#81B28A',
  successBackground: 'rgba(129, 178, 138, 0.15)',
  successText: '#A8C9B0',
  warning: '#E0A534',
  warningBackground: 'rgba(224, 165, 52, 0.15)',
  warningText: '#FAD67A',
  error: '#E56D63',
  errorBackground: 'rgba(229, 109, 99, 0.15)',
  errorText: '#F08B81',
  info: '#2f7e98',
  infoBackground: 'rgba(107, 163, 182, 0.15)',
  infoText: '#A8C9B0',

  // Interactive & Controls
  borderFocus: '#81B28A',
  divider: '#1F2621',
  inputBackground: '#161C18',
  inputBorder: '#2A332E',
  placeholder: '#6D776F',
  disabled: '#1F2621',
  disabledText: '#6D776F',

  // Navigation & Tab Bar
  tabBarBackground: '#0E1411',
  tabBarActive: '#81B28A',
  tabBarInactive: '#6D776F',
  tabBarBorder: '#1F2621',

  // Domain Specific (Care Actions)
  careWater: '#5FA79A',
  careFertilize: '#9BB896',
  carePrune: '#371c65',
  careHarvest: '#81B28A',
};

export const themeColors = {
  light: lightTheme,
  dark: darkTheme,
};


// -----------------------------------------------------------------------------
// 3. CENTRALIZED EXPORTS
// -----------------------------------------------------------------------------
export const colorConfig = {
  palette,
  theme: themeColors,
  light: lightTheme,
  dark: darkTheme,
} as const;

export const Colors = colorConfig;


// -----------------------------------------------------------------------------
// 4. TYPES & HELPER UTILITIES
// -----------------------------------------------------------------------------
export type ThemeMode = 'light' | 'dark';
export type ThemeColor = keyof ThemeColors;
export type ColorPalette = typeof palette;

/**
 * Returns theme colors based on scheme name ('light' | 'dark' | null | undefined)
 */
export function getThemeColors(scheme?: ColorSchemeName): ThemeColors {
  const mode: ThemeMode = scheme === 'dark' ? 'dark' : 'light';
  return themeColors[mode];
}

/**
 * Utility to convert Hex color to RGBA with dynamic opacity
 */
export function hexToRgba(hex: string, alpha: number = 1): string {
  const cleanHex = hex.replace('#', '');
  const r = parseInt(cleanHex.substring(0, 2), 16) || 0;
  const g = parseInt(cleanHex.substring(2, 4), 16) || 0;
  const b = parseInt(cleanHex.substring(4, 6), 16) || 0;
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

export default colorConfig;
