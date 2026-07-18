import React from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  FlatList,
  Dimensions,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useData } from '@/context/DataContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';

export default function HomeScreen() {
  const {
    plants,
    locations,
    notifications,
    needsWater,
    waterOne,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const dueCrops = needsWater.filter((p) => p.needs_water);
  const unreadAlerts = notifications.filter((n) => !n.is_read);

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  // Render Saved Layout Grid Matrix
  const renderLayoutGrid = () => {
    const positionedPlants = plants.filter(
      (p) => p.bed_x !== null && p.bed_y !== null && p.bed_x !== undefined && p.bed_y !== undefined
    );

    if (positionedPlants.length === 0) {
      return (
        <ThemedView type="backgroundElement" style={styles.emptyGridCard}>
          <SymbolView name="grid" size={32} tintColor="#888" />
          <ThemedText themeColor="textSecondary" style={styles.emptyGridText}>
            No plants assigned to layout positions yet.
          </ThemedText>
        </ThemedView>
      );
    }

    const maxBedX = Math.max(...positionedPlants.map((p) => Number(p.bed_x)));
    const maxBedY = Math.max(...positionedPlants.map((p) => Number(p.bed_y)));

    const grid: (any | null)[][] = Array.from({ length: maxBedY + 1 }, () =>
      Array.from({ length: maxBedX + 1 }, () => null)
    );

    positionedPlants.forEach((plant) => {
      const x = Number(plant.bed_x);
      const y = Number(plant.bed_y);
      if (y < grid.length && x < grid[y].length) {
        grid[y][x] = plant;
      }
    });

    return (
      <ScrollView horizontal contentContainerStyle={{ paddingBottom: Spacing.two }}>
        <View style={styles.gridContainer}>
          {grid.map((row, y) => (
            <View key={`row-${y}`} style={styles.gridRow}>
              {row.map((plant, x) => (
                <View
                  key={`cell-${x}-${y}`}
                  style={[
                    styles.gridCell,
                    plant ? styles.gridCellOccupied : styles.gridCellEmpty,
                  ]}
                >
                  {plant ? (
                    <>
                      <ThemedText style={styles.gridPlantName} numberOfLines={1}>
                        {plant.name}
                      </ThemedText>
                      <ThemedText style={styles.gridPlantLoc}>
                        {`B${x + 1} R${y + 1}`}
                      </ThemedText>
                    </>
                  ) : (
                    <ThemedText style={styles.gridCellEmptyText}>-</ThemedText>
                  )}
                </View>
              ))}
            </View>
          ))}
        </View>
      </ScrollView>
    );
  };

  if (loading && plants.length === 0) {
    return (
      <ThemedView style={styles.center}>
        <ActivityIndicator size="large" color="#10B981" />
      </ThemedView>
    );
  }

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        <ScrollView
          contentContainerStyle={styles.scrollContainer}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
          }
        >
          {/* Header */}
          <View style={styles.header}>
            <View>
              <ThemedText type="subtitle" style={styles.title}>
                Overview
              </ThemedText>
              <ThemedText themeColor="textSecondary">
                Live farm vitals and alerts
              </ThemedText>
            </View>
            <TouchableOpacity onPress={refreshAll} style={styles.refreshButton}>
              <SymbolView name="arrow.clockwise" size={20} tintColor="#10B981" />
            </TouchableOpacity>
          </View>

          {/* Quick Metrics Grid */}
          <View style={styles.metricsGrid}>
            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="leaf" size={24} tintColor="#10B981" />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {plants.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Plants
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="mappin.and.ellipse" size={24} tintColor="#3B82F6" />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {locations.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Locations
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="drop.fill" size={24} tintColor="#06B6D4" />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {dueCrops.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Needs Water
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="bell.badge.fill" size={24} tintColor="#EF4444" />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {unreadAlerts.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Alerts
              </ThemedText>
            </ThemedView>
          </View>

          {/* Watering Queue */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <ThemedText type="smallBold" style={styles.sectionTitle}>
                Watering Queue
              </ThemedText>
              {dueCrops.length > 6 && (
                <ThemedText themeColor="textSecondary" type="small">
                  showing top 6
                </ThemedText>
              )}
            </View>

            {dueCrops.length === 0 ? (
              <ThemedView type="backgroundElement" style={styles.emptyCard}>
                <SymbolView name="checkmark.circle.fill" size={24} tintColor="#10B981" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  All plants are hydrated. No due tasks!
                </ThemedText>
              </ThemedView>
            ) : (
              dueCrops.slice(0, 6).map((item) => (
                <ThemedView
                  key={`due-${item.plant_id}`}
                  type="backgroundElement"
                  style={styles.queueItem}
                >
                  <View style={{ flex: 1 }}>
                    <ThemedText type="smallBold">{item.name}</ThemedText>
                    <ThemedText themeColor="textSecondary" style={styles.queueSub}>
                      Last watered: {formatDate(item.last_watered)}
                    </ThemedText>
                  </View>
                  <TouchableOpacity
                    style={styles.waterButton}
                    onPress={() => waterOne(item.plant_id)}
                  >
                    <SymbolView name="drop.fill" size={14} tintColor="#fff" />
                    <ThemedText style={styles.waterButtonText}>Water</ThemedText>
                  </TouchableOpacity>
                </ThemedView>
              ))
            )}
          </View>

          {/* Saved Layout Visual Grid */}
          <View style={styles.section}>
            <ThemedText type="smallBold" style={styles.sectionTitle}>
              Saved Bed Layout
            </ThemedText>
            {renderLayoutGrid()}
          </View>

          {/* Recent Notifications */}
          <View style={styles.section}>
            <ThemedText type="smallBold" style={styles.sectionTitle}>
              Recent Notifications
            </ThemedText>
            {notifications.length === 0 ? (
              <ThemedView type="backgroundElement" style={styles.emptyCard}>
                <SymbolView name="envelope.open.fill" size={24} tintColor="#888" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  No notifications.
                </ThemedText>
              </ThemedView>
            ) : (
              notifications.slice(0, 5).map((noti) => (
                <ThemedView
                  key={`noti-${noti.id}`}
                  type="backgroundElement"
                  style={[styles.notiItem, !noti.is_read && styles.notiUnread]}
                >
                  <View style={styles.notiHeaderLine}>
                    <ThemedText type="smallBold" style={{ flex: 1 }}>
                      {noti.message}
                    </ThemedText>
                    <View style={[styles.statusBadge, noti.is_read ? styles.badgeRead : styles.badgeUnread]}>
                      <ThemedText style={styles.statusBadgeText}>
                        {noti.is_read ? 'Read' : 'New'}
                      </ThemedText>
                    </View>
                  </View>
                  <ThemedText themeColor="textSecondary" style={styles.notiTime}>
                    {formatDate(noti.created_at)}
                  </ThemedText>
                </ThemedView>
              ))
            )}
          </View>
        </ScrollView>
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
  scrollContainer: {
    paddingHorizontal: Spacing.three,
    paddingTop: Spacing.two,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.four,
  },
  title: {
    fontWeight: 'bold',
  },
  refreshButton: {
    padding: Spacing.two,
    borderRadius: 20,
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.two,
    marginBottom: Spacing.four,
  },
  metricCard: {
    width: '47%',
    flexGrow: 1,
    padding: Spacing.three,
    borderRadius: Spacing.three,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 100,
  },
  metricValue: {
    fontWeight: 'bold',
    fontSize: 24,
    marginVertical: Spacing.half,
  },
  metricLabel: {
    fontSize: 12,
  },
  section: {
    marginBottom: Spacing.four,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    marginBottom: Spacing.two,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: Spacing.two,
  },
  emptyCard: {
    padding: Spacing.four,
    borderRadius: Spacing.three,
    alignItems: 'center',
    gap: Spacing.one,
  },
  emptyText: {
    fontSize: 14,
    textAlign: 'center',
  },
  queueItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.two,
  },
  queueSub: {
    fontSize: 12,
    marginTop: Spacing.half,
  },
  waterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#06B6D4',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.one,
  },
  waterButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  emptyGridCard: {
    padding: Spacing.five,
    borderRadius: Spacing.three,
    alignItems: 'center',
    gap: Spacing.two,
  },
  emptyGridText: {
    fontSize: 14,
    textAlign: 'center',
  },
  gridContainer: {
    padding: Spacing.two,
    backgroundColor: 'rgba(0,0,0,0.03)',
    borderRadius: Spacing.three,
    gap: Spacing.one,
  },
  gridRow: {
    flexDirection: 'row',
    gap: Spacing.one,
  },
  gridCell: {
    width: 80,
    height: 80,
    borderRadius: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.one,
  },
  gridCellOccupied: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderWidth: 1.5,
    borderColor: '#10B981',
  },
  gridCellEmpty: {
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.1)',
  },
  gridPlantName: {
    fontSize: 11,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  gridPlantLoc: {
    fontSize: 9,
    color: '#666',
    marginTop: 2,
  },
  gridCellEmptyText: {
    fontSize: 16,
    color: '#aaa',
  },
  notiItem: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.two,
  },
  notiUnread: {
    borderLeftWidth: 4,
    borderLeftColor: '#EF4444',
  },
  notiHeaderLine: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: Spacing.two,
  },
  notiTime: {
    fontSize: 11,
    marginTop: Spacing.one,
  },
  statusBadge: {
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 8,
  },
  badgeRead: {
    backgroundColor: '#E5E7EB',
  },
  badgeUnread: {
    backgroundColor: '#FEE2E2',
  },
  statusBadgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#374151',
  },
});
