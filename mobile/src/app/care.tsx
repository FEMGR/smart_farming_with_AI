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

export default function CareScreen() {
  const {
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

  const [activeSegment, setActiveSegment] = useState<'irrigation' | 'notifications'>('irrigation');
  const [actionLoading, setActionLoading] = useState(false);

  const duePlants = needsWater.filter((p) => p.needs_water);
  const currentPlants = needsWater.filter((p) => !p.needs_water);

  const handleWaterAll = async () => {
    if (duePlants.length === 0) {
      Alert.alert('Info', 'All plants are already hydrated!');
      return;
    }

    Alert.alert(
      'Water All Due',
      `Are you sure you want to mark all ${duePlants.length} due plants as watered?`,
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
          <TouchableOpacity onPress={refreshAll} style={styles.refreshBtn}>
            <SymbolView name="arrow.clockwise" size={20} tintColor="#10B981" />
          </TouchableOpacity>
        </View>

        {/* Segmented Controller */}
        <View style={styles.segmentedContainer}>
          <TouchableOpacity
            style={[styles.segmentBtn, activeSegment === 'irrigation' && styles.segmentBtnActive]}
            onPress={() => setActiveSegment('irrigation')}
          >
            <SymbolView
              name="drop.fill"
              size={14}
              tintColor={activeSegment === 'irrigation' ? '#10B981' : '#888'}
            />
            <ThemedText style={[styles.segmentText, activeSegment === 'irrigation' && styles.segmentTextActive]}>
              Irrigation ({duePlants.length} Due)
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segmentBtn, activeSegment === 'notifications' && styles.segmentBtnActive]}
            onPress={() => setActiveSegment('notifications')}
          >
            <SymbolView
              name="bell.fill"
              size={14}
              tintColor={activeSegment === 'notifications' ? '#10B981' : '#888'}
            />
            <ThemedText style={[styles.segmentText, activeSegment === 'notifications' && styles.segmentTextActive]}>
              Alerts ({notifications.filter((n) => !n.is_read).length} New)
            </ThemedText>
          </TouchableOpacity>
        </View>

        {/* List Content */}
        {loading && needsWater.length === 0 ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : activeSegment === 'irrigation' ? (
          <View style={{ flex: 1 }}>
            {/* Quick Actions for Irrigation */}
            <View style={styles.careActionsRow}>
              <TouchableOpacity style={styles.careActionBtn} onPress={refreshAll}>
                <SymbolView name="arrow.clockwise" size={14} tintColor="#10B981" />
                <ThemedText style={styles.careActionText}>Check status</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.careActionBtn, styles.waterAllBtn]}
                onPress={handleWaterAll}
                disabled={actionLoading}
              >
                <SymbolView name="drop.fill" size={14} tintColor="#fff" />
                <ThemedText style={[styles.careActionText, { color: '#fff' }]}>Water all due</ThemedText>
              </TouchableOpacity>
            </View>

            <ScrollView
              contentContainerStyle={styles.scrollList}
              refreshControl={
                <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
              }
            >
              {/* Due Category */}
              <ThemedText type="smallBold" style={styles.categoryTitle}>
                Due for Watering ({duePlants.length})
              </ThemedText>
              {duePlants.length === 0 ? (
                <ThemedView type="backgroundElement" style={styles.emptyCard}>
                  <SymbolView name="checkmark.seal.fill" size={32} tintColor="#10B981" />
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
                      style={styles.waterOneBtn}
                      onPress={() => handleWaterOne(plant.plant_id, plant.name)}
                      disabled={actionLoading}
                    >
                      <SymbolView name="drop.fill" size={12} tintColor="#fff" />
                      <ThemedText style={styles.waterOneBtnText}>Water</ThemedText>
                    </TouchableOpacity>
                  </ThemedView>
                ))
              )}

              {/* Current Category */}
              {currentPlants.length > 0 && (
                <>
                  <ThemedText type="smallBold" style={[styles.categoryTitle, { marginTop: Spacing.four }]}>
                    Hydrated / Current ({currentPlants.length})
                  </ThemedText>
                  {currentPlants.map((plant) => (
                    <ThemedView key={`current-${plant.plant_id}`} type="backgroundElement" style={[styles.careCard, { opacity: 0.7 }]}>
                      <View style={{ flex: 1 }}>
                        <ThemedText type="smallBold">{plant.name}</ThemedText>
                        <ThemedText themeColor="textSecondary" style={styles.careCardSub}>
                          Hydrated · Last watered: {formatDate(plant.last_watered)}
                        </ThemedText>
                      </View>
                      <SymbolView name="checkmark.circle.fill" size={20} tintColor="#10B981" />
                    </ThemedView>
                  ))}
                </>
              )}
            </ScrollView>
          </View>
        ) : (
          /* ALERTS (NOTIFICATIONS) VIEW */
          <ScrollView
            contentContainerStyle={styles.scrollList}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {notifications.length === 0 ? (
              <View style={styles.empty}>
                <SymbolView name="bell.slash.fill" size={48} tintColor="#ccc" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  No notifications or alerts.
                </ThemedText>
              </View>
            ) : (
              notifications.map((noti) => (
                <ThemedView
                  key={noti.id}
                  type="backgroundElement"
                  style={[styles.notiCard, !noti.is_read && styles.notiUnread]}
                >
                  <View style={styles.notiContent}>
                    <View style={styles.notiHeader}>
                      <ThemedText type="smallBold" style={styles.notiMsg}>
                        {noti.message}
                      </ThemedText>
                      <View style={[styles.badge, noti.is_read ? styles.badgeRead : styles.badgeUnread]}>
                        <ThemedText style={styles.badgeText}>{noti.is_read ? 'Read' : 'New'}</ThemedText>
                      </View>
                    </View>
                    
                    <ThemedText themeColor="textSecondary" style={styles.notiMeta}>
                      {getNotificationLocLabel(noti)} • {formatDate(noti.created_at)}
                    </ThemedText>
                  </View>

                  {!noti.is_read && (
                    <TouchableOpacity
                      style={styles.markReadBtn}
                      onPress={() => handleMarkRead(noti.id)}
                    >
                      <SymbolView name="checkmark" size={14} tintColor="#10B981" />
                      <ThemedText style={styles.markReadText}>Mark read</ThemedText>
                    </TouchableOpacity>
                  )}
                </ThemedView>
              ))
            )}
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
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  segmentedContainer: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.05)',
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
    backgroundColor: '#fff',
    ...Platform.select({
      web: {
        boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
      },
      default: {
        shadowColor: '#000',
        shadowOpacity: 0.1,
        shadowOffset: { width: 0, height: 1 },
        shadowRadius: 2,
        elevation: 1,
      },
    }),
  },
  segmentText: {
    fontSize: 13,
    color: '#666',
  },
  segmentTextActive: {
    color: '#10B981',
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
    borderColor: '#10B981',
    borderRadius: Spacing.two,
    paddingVertical: Spacing.two,
    gap: Spacing.one,
  },
  waterAllBtn: {
    backgroundColor: '#06B6D4',
    borderColor: '#06B6D4',
  },
  careActionText: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#10B981',
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
    backgroundColor: '#06B6D4',
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.half,
  },
  waterOneBtnText: {
    color: '#fff',
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
  notiUnread: {
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444',
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
  badgeRead: {
    backgroundColor: '#E5E7EB',
  },
  badgeUnread: {
    backgroundColor: '#FEE2E2',
  },
  badgeText: {
    fontSize: 9,
    fontWeight: 'bold',
    color: '#374151',
  },
  markReadBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
    marginTop: Spacing.two,
    paddingTop: Spacing.two,
    gap: Spacing.one,
  },
  markReadText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#10B981',
  },
});
