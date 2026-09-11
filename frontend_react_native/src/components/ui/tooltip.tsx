import React, { useState } from 'react';
import { View, StyleSheet, Pressable, Platform, StyleProp, ViewStyle } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { useTheme } from '@/hooks/use-theme';
import { TOOLTIP_NOTES, TooltipKey } from '@/constants/tooltips';

export interface TooltipProps {
  /**
   * Key mapping to centralized TOOLTIP_NOTES registry
   */
  id?: TooltipKey;
  /**
   * Custom text override or manual string note
   */
  text?: string;
  /**
   * Child component (e.g. TouchableOpacity, View, Icon) to attach tooltip to
   */
  children: React.ReactNode;
  /**
   * Position of tooltip bubble relative to child
   * @default 'top'
   */
  position?: 'top' | 'bottom' | 'left' | 'right';
  /**
   * Horizontal alignment of tooltip bubble
   * @default 'center'
   */
  align?: 'center' | 'left' | 'right';
  /**
   * Additional style for wrapper container
   */
  style?: StyleProp<ViewStyle>;
}

export function Tooltip({
  id,
  text,
  children,
  position = 'top',
  align = 'center',
  style,
}: TooltipProps) {
  const colors = useTheme();
  const [visible, setVisible] = useState(false);

  const noteText = text ?? (id ? TOOLTIP_NOTES[id] : undefined);

  if (!noteText) {
    return <>{children}</>;
  }

  const getPositionStyle = (): ViewStyle => {
    switch (position) {
      case 'bottom':
        return {
          top: '100%',
          marginTop: 6,
        };
      case 'left':
        return {
          right: '100%',
          marginRight: 6,
          top: '50%',
        };
      case 'right':
        return {
          left: '100%',
          marginLeft: 6,
          top: '50%',
        };
      case 'top':
      default:
        return {
          bottom: '100%',
          marginBottom: 6,
        };
    }
  };

  const getAlignStyle = (): ViewStyle => {
    if (position === 'left' || position === 'right') return {};
    switch (align) {
      case 'left':
        return { left: 0 };
      case 'right':
        return { right: 0 };
      case 'center':
      default:
        return {
          alignSelf: 'center',
        };
    }
  };

  return (
    <View
      style={[styles.wrapper, style]}
      // @ts-ignore Web pointer enter/leave support
      onPointerEnter={() => setVisible(true)}
      // @ts-ignore
      onPointerLeave={() => setVisible(false)}
    >
      <Pressable
        onHoverIn={() => setVisible(true)}
        onHoverOut={() => setVisible(false)}
        // @ts-ignore Native web tooltip attribute fallback
        title={Platform.OS === 'web' ? noteText : undefined}
      >
        {children}
      </Pressable>

      {visible && (
        <View
          pointerEvents="none"
          style={[
            styles.tooltipBubble,
            {
              backgroundColor: colors.isDark ? '#2A332E' : '#1F2A22',
              borderColor: colors.border,
            },
            getPositionStyle(),
            getAlignStyle(),
          ]}
        >
          <ThemedText style={styles.tooltipText}>{noteText}</ThemedText>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'relative',
    zIndex: 999,
  },
  tooltipBubble: {
    position: 'absolute',
    paddingVertical: 5,
    paddingHorizontal: 10,
    borderRadius: 6,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 6,
    zIndex: 9999,
    maxWidth: 220,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tooltipText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '600',
    textAlign: 'center',
  },
});

export default Tooltip;
