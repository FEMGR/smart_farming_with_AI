import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useData } from '@/context/DataContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';
import { useTheme } from '@/hooks/use-theme';

export default function CareScreen() {
  const colors = useTheme();
  const {
    plants,
    needsWater,
    notifications,
    locations,
    waterOne,
    waterAll,
    readNotification,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const [expandedSection, setExpandedSection] = useState<string | null>('due');
  const [actionLoading, setActionLoading] = useState(false);

  const duePlants = needsWater.filter((p) => p.needs_water);
  const currentPlants = plants.filter(
    (p) => !duePlants.some((d) => (d.plant_id ?? d.id) === p.id)
  );

  const totalCareTasks = plants.length || needsWater.length || 0;
  const finishedCareTasks = Math.max(0, totalCareTasks - duePlants.length);
  const careProgress = totalCareTasks === 0 ? 1 : Math.min(1, Math.max(0, finishedCareTasks / totalCareTasks));

  const totalNotis = notifications.length || 1;
  const readNotis = notifications.filter((n) => n.is_read).length;
  const notiProgress = Math.min(1, Math.max(0, readNotis / totalNotis));

  const renderAccordionHeader = (
    id: string,
    title: string,
    dueText: string,
    finishedCount: number,
    totalCount: number,
    progress: number
  ) => {
    const isOpen = expandedSection === id;
    const progressPercent = Math.round(progress * 100);

    return (
      <TouchableOpacity
        activeOpacity={0.8}
        onPress={() => setExpandedSection(isOpen ? null : id)}
        style={[
          styles.accordionHeaderCard,
          {
            backgroundColor: isOpen ? colors.badgeSuccessBackground : colors.backgroundElement,
            borderColor: colors.border,
          },
          isOpen && styles.accordionHeaderCardActive,
        ]}
      >
        <View style={styles.accordionHeaderLeft}>
          <ThemedText type="smallBold" style={styles.accordionTitleText}>
            {title}
          </ThemedText>
        </View>

        <View style={styles.accordionHeaderRight}>
          <View style={styles.accordionMetaColumn}>
            <ThemedText themeColor="textSecondary" style={styles.accordionDueText}>
              {dueText}
            </ThemedText>
            <View style={styles.accordionProgressRow}>
              <View style={[styles.accordionProgressBarTrack, { backgroundColor: colors.disabled }]}>
                <View
                  style={[
                    styles.accordionProgressBarFill,
                    { width: `${progressPercent}%`, backgroundColor: colors.emerald },
                  ]}
                />
              </View>
              <ThemedText themeColor="textSecondary" style={styles.accordionRatioText}>
                {`${finishedCount}/${totalCount} (${progressPercent}%)`}
              </ThemedText>
            </View>
          </View>

          <View style={styles.arrowIconWrapper}>
            <SymbolView
              name={isOpen ? 'chevron.up' : 'chevron.down'}
              size={18}
              tintColor={colors.emerald}
            />
          </View>
        </View>
      </TouchableOpacity>
    );
  };


  const handleWaterAll = async () => {
    if (duePlants.length === 0) {
      Alert.alert('Info', 'All plants are already hydrated!');
      return;
    }

    const message = `Are you sure you want to mark all ${duePlants.length} due plants as watered?`;

    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined' && window.confirm(message)) {
        setActionLoading(true);
        try {
          const res = await waterAll();
          const count = res?.count || duePlants.length;
          Alert.alert('Success', `${count} plant(s) watered. All due tasks are now cleared.`);
        } catch (e: any) {
          Alert.alert('Error', e.message || 'Failed to water all due plants');
        } finally {
          setActionLoading(false);
        }
      }
      return;
    }

    Alert.alert(
      'Water All Due',
      message,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Water All',
          onPress: async () => {
            setActionLoading(true);
            try {
              const res = await waterAll();
              const count = res?.count || duePlants.length;
              Alert.alert('Success', `${count} plant(s) watered. All due tasks are now cleared.`);
            } catch (e: any) {
              Alert.alert('Error', e.message || 'Failed to water all due plants');
            } finally {
              setActionLoading(false);
            }
          },
        },
      ]
    );
  };

  const handleWaterOne = async (plantId: number, name: string) => {
    setActionLoading(true);
    try {
      await waterOne(plantId);
      Alert.alert('Success', `${name} marked as watered.`);
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to water plant');
    } finally {
      setActionLoading(false);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    try {
      await readNotification(notificationId);
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to mark notification as read');
    }
  };

  const getNotificationLocLabel = (noti: any) => {
    const plant = noti.plant || {};
    const bedX = plant.bed_x;
    const bedY = plant.bed_y;
    const loc = plant.location || {};
    
    const parts = [];
    if (bedX !== null && bedX !== undefined && bedY !== null && bedY !== undefined) {
      parts.push(`Bed ${Number(bedX) + 1} Row ${Number(bedY) + 1}`);
    }
    const locationName = loc.name || locations.find((l) => l.id === plant.location_id)?.name;
    if (locationName) {
      parts.push(locationName);
    }

    if (parts.length > 0) {
      return parts.join(' • ');
    }
    return noti.type ? String(noti.type).toUpperCase() : 'ALERT';
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    try {
      return new Date(dateStr).toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <ThemedText type="subtitle" style={styles.title}>
              Care Center
            </ThemedText>
            <ThemedText themeColor="textSecondary">
              Manage irrigation and review alert history
            </ThemedText>
          </View>
          <TouchableOpacity onPress={refreshAll} style={[styles.refreshBtn, { backgroundColor: colors.badgeSuccessBackground }]}>
            <SymbolView name="arrow.clockwise" size={20} tintColor={colors.emerald} />
          </TouchableOpacity>
        </View>

        {/* List Content */}
        {loading && needsWater.length === 0 ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color={colors.emerald} />
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={styles.scrollList}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {/* Accordion 1: Due for Watering */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'due',
                'Watering Tasks (Due)',
                `Due: ${duePlants.length} pending`,
                finishedCareTasks,
                totalCareTasks,
                careProgress
              )}

              {expandedSection === 'due' && (
                <View style={{ paddingTop: Spacing.two }}>
                  <View style={styles.careActionsRow}>
                    <TouchableOpacity style={[styles.careActionBtn, { borderColor: colors.emerald }]} onPress={refreshAll}>
                      <SymbolView name="arrow.clockwise" size={14} tintColor={colors.emerald} />
                      <ThemedText style={[styles.careActionText, { color: colors.emerald }]}>Check status</ThemedText>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.careActionBtn, styles.waterAllBtn, { backgroundColor: colors.careWater, borderColor: colors.careWater }]}
                      onPress={handleWaterAll}
                      disabled={actionLoading}
                    >
                      <SymbolView name="drop.fill" size={14} tintColor={colors.textInverse} />
                      <ThemedText style={[styles.careActionText, { color: colors.textInverse }]}>Water all due</ThemedText>
                    </TouchableOpacity>
                  </View>

                  {duePlants.length === 0 ? (
                    <ThemedView type="backgroundElement" style={styles.emptyCard}>
                      <SymbolView name="checkmark.seal.fill" size={32} tintColor={colors.emerald} />
                      <ThemedText themeColor="textSecondary">All plants are current and watered.</ThemedText>
                    </ThemedView>
                  ) : (
                    duePlants.map((plant) => (
                      <ThemedView key={`due-${plant.plant_id}`} type="backgroundElement" style={styles.careCard}>
                        <View style={{ flex: 1 }}>
                          <ThemedText type="smallBold">{plant.name}</ThemedText>
                          <ThemedText themeColor="textSecondary" style={styles.careCardSub}>
                            Interval: {plant.watering_interval_days || 4} days · Last watered: {formatDate(plant.last_watered)}
                          </ThemedText>
                        </View>
                        <TouchableOpacity
                          style={[styles.waterOneBtn, { backgroundColor: colors.careWater }]}
                          onPress={() => handleWaterOne(plant.plant_id, plant.name)}
                          disabled={actionLoading}
                        >
                          <SymbolView name="drop.fill" size={12} tintColor={colors.textInverse} />
                          <ThemedText style={[styles.waterOneBtnText, { color: colors.textInverse }]}>Water</ThemedText>
                        </TouchableOpacity>
                      </ThemedView>
                    ))
                  )}
                </View>
              )}
            </View>

            {/* Accordion 2: Hydrated / Current */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'current',
                'Hydrated & Current Crops',
                `Current: ${currentPlants.length} plants`,
                currentPlants.length,
                totalCareTasks,
                currentPlants.length > 0 ? 1.0 : 0.0
              )}

              {expandedSection === 'current' && (
                <View style={{ paddingTop: Spacing.two }}>
                  {currentPlants.length === 0 ? (
                    <ThemedView type="backgroundElement" style={styles.emptyCard}>
                      <ThemedText themeColor="textSecondary">No plants currently marked as hydrated.</ThemedText>
                    </ThemedView>
                  ) : (
                    currentPlants.map((plant) => (
                      <ThemedView key={`cur-${plant.plant_id}`} type="backgroundElement" style={styles.careCard}>
                        <View style={{ flex: 1 }}>
                          <ThemedText type="smallBold">{plant.name}</ThemedText>
                          <ThemedText themeColor="textSecondary" style={styles.careCardSub}>
                            Last watered: {formatDate(plant.last_watered)}
                          </ThemedText>
                        </View>
                      </ThemedView>
                    ))
                  )}
                </View>
              )}
            </View>

            {/* Accordion 3: Alerts & Notifications */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'notifications',
                'Alerts & Care History',
                `Alerts: ${notifications.filter((n) => !n.is_read).length} unread`,
                readNotis,
                totalNotis,
                notiProgress
              )}

              {expandedSection === 'notifications' && (
                <View style={{ paddingTop: Spacing.two }}>
                  {notifications.length === 0 ? (
                    <ThemedView type="backgroundElement" style={styles.emptyCard}>
                      <SymbolView name="bell.slash.fill" size={32} tintColor={colors.placeholder} />
                      <ThemedText themeColor="textSecondary">No notifications or alerts.</ThemedText>
                    </ThemedView>
                  ) : (
                    notifications.map((noti) => (
                      <ThemedView
                        key={`noti-full-${noti.id}`}
                        type="backgroundElement"
                        style={[styles.notiCard, !noti.is_read && { borderLeftWidth: 4, borderLeftColor: colors.badgeErrorText }]}
                      >
                        <View style={styles.notiContent}>
                          <View style={styles.notiHeader}>
                            <ThemedText type="smallBold" style={styles.notiMsg}>
                              {noti.message}
                            </ThemedText>
                            <View style={[styles.badge, noti.is_read ? { backgroundColor: colors.disabled } : { backgroundColor: colors.badgeErrorBackground }]}>
                              <ThemedText style={[styles.badgeText, { color: noti.is_read ? colors.textSecondary : colors.badgeErrorText }]}>{noti.is_read ? 'READ' : 'NEW'}</ThemedText>
                            </View>
                          </View>
                          <ThemedText themeColor="textSecondary" style={styles.notiMeta}>
                            {getNotificationLocLabel(noti)} · {formatDate(noti.created_at)}
                          </ThemedText>
                        </View>

                        {!noti.is_read && (
                          <TouchableOpacity
                            style={[styles.markReadBtn, { borderTopColor: colors.divider }]}
                            onPress={() => handleMarkRead(noti.id)}
                          >
                            <SymbolView name="checkmark.circle.fill" size={14} tintColor={colors.emerald} />
                            <ThemedText style={[styles.markReadText, { color: colors.emerald }]}>Mark as Read</ThemedText>
                          </TouchableOpacity>
                        )}
                      </ThemedView>
                    ))
                  )}
                </View>
              )}
            </View>
          </ScrollView>
        )}
      </SafeAreaView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: Spacing.three,
    paddingTop: Spacing.two,
    marginBottom: Spacing.three,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  title: {
    fontWeight: 'bold',
  },
  refreshBtn: {
    padding: Spacing.two,
    borderRadius: 20,
  },
  segmentedContainer: {
    flexDirection: 'row',
    borderRadius: Spacing.two,
    marginHorizontal: Spacing.three,
    marginBottom: Spacing.three,
    padding: 2,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '90%',
  },
  segmentBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.two,
    borderRadius: Spacing.two,
    gap: Spacing.one,
  },
  segmentBtnActive: {
    ...Platform.select({
      web: {
        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
      },
      default: {
        shadowOpacity: 0.1,
        shadowOffset: { width: 0, height: 1 },
        shadowRadius: 2,
        elevation: 1,
      },
    }),
  },
  segmentText: {
    fontSize: 13,
  },
  segmentTextActive: {
    fontWeight: 'bold',
  },
  careActionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: Spacing.three,
    marginBottom: Spacing.three,
    gap: Spacing.two,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  careActionBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderRadius: Spacing.two,
    paddingVertical: Spacing.two,
    gap: Spacing.one,
  },
  waterAllBtn: {},
  careActionText: {
    fontSize: 13,
    fontWeight: 'bold',
  },
  scrollList: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  categoryTitle: {
    fontSize: 16,
    marginBottom: Spacing.two,
  },
  emptyCard: {
    padding: Spacing.five,
    borderRadius: Spacing.three,
    alignItems: 'center',
    gap: Spacing.two,
  },
  careCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.two,
  },
  careCardSub: {
    fontSize: 11,
    marginTop: 2,
  },
  waterOneBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.half,
  },
  waterOneBtnText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: Spacing.six,
  },
  emptyText: {
    fontSize: 14,
    marginTop: Spacing.two,
    textAlign: 'center',
  },
  notiCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.three,
  },
  notiContent: {
    flex: 1,
  },
  notiHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: Spacing.two,
  },
  notiMsg: {
    fontSize: 14,
    flex: 1,
  },
  notiMeta: {
    fontSize: 11,
    marginTop: Spacing.one,
  },
  badge: {
    paddingVertical: 1,
    paddingHorizontal: 5,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 9,
    fontWeight: 'bold',
  },
  markReadBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    marginTop: Spacing.two,
    paddingTop: Spacing.two,
    gap: Spacing.one,
  },
  markReadText: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  accordionHeaderCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.three,
    borderRadius: Spacing.three,
    borderWidth: 1,
  },
  accordionHeaderCardActive: {
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    borderBottomWidth: 0,
  },
  accordionHeaderLeft: {
    flex: 1.1,
    paddingRight: Spacing.two,
  },
  accordionTitleText: {
    fontSize: 15,
  },
  accordionHeaderRight: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: Spacing.two,
  },
  accordionMetaColumn: {
    alignItems: 'flex-end',
  },
  accordionDueText: {
    fontSize: 11,
    fontWeight: '600',
    marginBottom: 2,
  },
  accordionProgressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.one,
  },
  accordionProgressBarTrack: {
    width: 60,
    height: 6,
    backgroundColor: 'rgba(128, 128, 128, 0.2)',
    borderRadius: 3,
    overflow: 'hidden',
  },
  accordionProgressBarFill: {
    height: '100%',
    borderRadius: 3,
  },
  accordionRatioText: {
    fontSize: 10,
    fontWeight: '500',
  },
  arrowIconWrapper: {
    padding: Spacing.one,
  },
});

