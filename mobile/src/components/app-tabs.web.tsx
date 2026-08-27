import {
  Tabs,
  TabList,
  TabTrigger,
  TabSlot,
  TabTriggerSlotProps,
  TabListProps,
} from 'expo-router/ui';
import { usePathname } from 'expo-router';
import { SymbolView } from 'expo-symbols';
import { useState, useEffect, useRef } from 'react';
import { Pressable, useColorScheme, useWindowDimensions, View, StyleSheet, Platform } from 'react-native';

import { ExternalLink } from './external-link';
import { ThemedText } from './themed-text';
import { ThemedView } from './themed-view';
import { useAuth } from '@/context/AuthContext';

import { Colors, MaxContentWidth, Spacing } from '@/constants/theme';

const COMPACT_NAV_WIDTH = 640;

export default function AppTabs() {
  return (
    <Tabs style={styles.tabsRoot}>
      <TabSlot style={styles.tabSlot} />
      <TabList asChild>
        <CustomTabList>
          <TabTrigger name="index" href="/" asChild>
            <TabButton>Overview</TabButton>
          </TabTrigger>
          <TabTrigger name="plants" href="/plants" asChild>
            <TabButton>Plants</TabButton>
          </TabTrigger>
          <TabTrigger name="planning" href="/planning" asChild>
            <TabButton>Planning</TabButton>
          </TabTrigger>
          <TabTrigger name="care" href="/care" asChild>
            <TabButton>Care</TabButton>
          </TabTrigger>
          <TabTrigger name="more" href="/more" asChild>
            <TabButton>More</TabButton>
          </TabTrigger>
        </CustomTabList>
      </TabList>
    </Tabs>
  );
}

export function TabButton({ children, isFocused, ...props }: TabTriggerSlotProps) {
  return (
    <Pressable {...props} style={({ pressed }) => pressed && styles.pressed}>
      <ThemedView
        type={isFocused ? 'backgroundSelected' : 'backgroundElement'}
        style={styles.tabButtonView}>
        <ThemedText type="small" themeColor={isFocused ? 'text' : 'textSecondary'}>
          {children}
        </ThemedText>
      </ThemedView>
    </Pressable>
  );
}

export function CustomTabList(props: TabListProps) {
  const { logout } = useAuth();
  const scheme = useColorScheme();
  const { width } = useWindowDimensions();
  const [menuOpen, setMenuOpen] = useState(false);
  const colors = Colors[scheme === 'unspecified' ? 'light' : scheme];
  const isCompact = width < COMPACT_NAV_WIDTH;
  const buttonRef = useRef<any>(null);
  const dropdownRef = useRef<any>(null);
  const pathname = usePathname();

  // Collapse menu when page path changes
  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (Platform.OS !== 'web' || !menuOpen) return;

    const handleOutsideClick = (e: MouseEvent) => {
      // If the click is on the menu button itself, let onPress toggle handle it.
      if (buttonRef.current && buttonRef.current.contains(e.target as Node)) {
        return;
      }

      // If the click is inside the dropdown, defer setting menuOpen(false)
      // to let navigation/link click handlers complete first.
      if (dropdownRef.current && dropdownRef.current.contains(e.target as Node)) {
        setTimeout(() => {
          setMenuOpen(false);
        }, 100);
        return;
      }

      setMenuOpen(false);
    };

    document.addEventListener('click', handleOutsideClick);
    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [menuOpen]);

  if (isCompact) {
    return (
      <View {...props} style={styles.tabListContainer}>
        <ThemedView type="backgroundElement" style={styles.compactContainer}>
          <ThemedText type="smallBold" style={styles.brandText}>
            Smart Farming
          </ThemedText>

          <Pressable
            ref={buttonRef}
            accessibilityRole="button"
            accessibilityLabel={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            onPress={() => setMenuOpen((open) => !open)}
            style={({ pressed }) => [styles.menuButton, pressed && styles.pressed]}
          >
            <SymbolView
              tintColor={colors.textInverse}
              name="line.3.horizontal"
              size={20}
            />
            <SymbolView
              tintColor={colors.textInverse}
              name={menuOpen ? 'chevron.up' : 'chevron.down'}
              size={14}
            />
          </Pressable>
        </ThemedView>

        {menuOpen && (
          <ThemedView ref={dropdownRef} type="backgroundElement" style={styles.dropdownMenu}>
            <View style={styles.dropdownItems}>{props.children}</View>

            <ExternalLink href="https://docs.expo.dev" asChild>
              <Pressable style={styles.dropdownExternalPressable}>
                <ThemedText type="link">Docs</ThemedText>
                <SymbolView
                  tintColor={colors.text}
                  name={{ ios: 'arrow.up.right.square', web: 'link' }}
                  size={12}
                />
              </Pressable>
            </ExternalLink>

            <Pressable style={styles.dropdownSignOutPressable} onPress={logout}>
              <SymbolView
                tintColor="#fff"
                name="rectangle.portrait.and.arrow.right"
                size={14}
              />
              <ThemedText style={styles.signOutText}>Sign Out</ThemedText>
            </Pressable>
          </ThemedView>
        )}
      </View>
    );
  }

  return (
    <View {...props} style={styles.tabListContainer}>
      <ThemedView type="backgroundElement" style={styles.innerContainer}>
        <ThemedText type="smallBold" style={styles.brandText}>
          Smart Farming
        </ThemedText>

        {props.children}

        <ExternalLink href="https://docs.expo.dev" style={styles.externalPressable}>
          <ThemedText type="link">Docs</ThemedText>
          <SymbolView
            tintColor={colors.text}
            name="link"
            size={12}
          />
        </ExternalLink>

        <Pressable
          style={[styles.signOutPressable, { backgroundColor: colors.errorBackground }]}
          onPress={logout}
        >
          <ThemedText style={{ color: colors.errorText, fontWeight: 'bold', fontSize: 13 }}>Sign Out</ThemedText>
          <SymbolView
            tintColor={colors.errorText}
            name="rectangle.portrait.and.arrow.right"
            size={14}
          />
        </Pressable>
      </ThemedView>
    </View>
  );
}

const styles = StyleSheet.create({
  tabsRoot: {
    flex: 1,
    minHeight: '100%',
  },
  tabSlot: {
    height: '100%',
    paddingTop: 80,
  },
  tabListContainer: {
    position: 'absolute',
    top: 0,
    width: '100%',
    padding: Spacing.three,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
  },
  innerContainer: {
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.five,
    borderRadius: Spacing.five,
    flexDirection: 'row',
    alignItems: 'center',
    flexGrow: 1,
    gap: Spacing.two,
    maxWidth: MaxContentWidth,
  },
  compactContainer: {
    paddingVertical: Spacing.two,
    paddingLeft: Spacing.four,
    paddingRight: Spacing.two,
    borderRadius: Spacing.four,
    flexDirection: 'row',
    alignItems: 'center',
    flexGrow: 1,
    gap: Spacing.two,
    maxWidth: MaxContentWidth,
  },
  brandText: {
    marginRight: 'auto',
  },
  pressed: {
    opacity: 0.7,
  },
  tabButtonView: {
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.three,
  },
  menuButton: {
    minWidth: 54,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: Spacing.one,
    paddingHorizontal: Spacing.two,
    backgroundColor: 'rgba(4, 220, 187, 0.32)',
  },
  dropdownMenu: {
    position: 'absolute',
    top: 70,
    left: Spacing.three,
    right: Spacing.three,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    borderRadius: Spacing.four,
    padding: Spacing.two,
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
  },
  dropdownItems: {
    gap: Spacing.one,
  },
  dropdownExternalPressable: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.one,
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    marginTop: Spacing.one,
  },
  dropdownSignOutPressable: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.one,
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    marginTop: Spacing.one,
    borderRadius: Spacing.two,
  },
  externalPressable: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: Spacing.one,
    marginLeft: Spacing.three,
  },
  signOutPressable: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.one,
    marginLeft: Spacing.one,
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.three,
  },
  signOutText: {
    fontSize: 13,
    fontWeight: '600',
  },
});
