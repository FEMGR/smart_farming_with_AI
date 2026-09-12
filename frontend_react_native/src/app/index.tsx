import React, { useState } from 'react';
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
import { useTheme } from '@/hooks/use-theme';
import { fetchCurrentWeather, WeatherData } from '@/services/weather';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';

export default function HomeScreen() {
  const themeColors = useTheme();
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

  const [expandedSection, setExpandedSection] = useState<string | null>('watering');

  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState<string | null>(null);

  const handleFetchWeather = async () => {
    setWeatherLoading(true);
    setWeatherError(null);
    try {
      const firstLoc = locations.find((l) => l.latitude && l.longitude);
      const data = await fetchCurrentWeather(
        firstLoc ? Number(firstLoc.latitude) : undefined,
        firstLoc ? Number(firstLoc.longitude) : undefined
      );
      setWeather(data);
    } catch (e: any) {
      setWeatherError(e.message || 'Failed to fetch weather data');
    } finally {
      setWeatherLoading(false);
    }
  };

  const dueCrops = needsWater.filter((p) => p.needs_water);
  const unreadAlerts = notifications.filter((n) => !n.is_read);

  // Calculations for progress & finished ratio
  const totalWaterTasks = plants.length || needsWater.length || 0;
  const finishedWaterTasks = Math.max(0, totalWaterTasks - dueCrops.length);
  const waterProgress = totalWaterTasks === 0 ? 1 : Math.min(1, Math.max(0, finishedWaterTasks / totalWaterTasks));

  const totalNotis = notifications.length || 1;
  const readNotis = notifications.filter((n) => n.is_read).length;
  const notiProgress = Math.min(1, Math.max(0, readNotis / totalNotis));

  const positionedPlantsCount = plants.filter(
    (p) => p.bed_x !== null && p.bed_y !== null && p.bed_x !== undefined && p.bed_y !== undefined
  ).length;
  const totalPlantsCount = plants.length || 1;
  const layoutProgress = Math.min(1, Math.max(0, positionedPlantsCount / totalPlantsCount));

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

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
            backgroundColor: isOpen ? themeColors.badgeSuccessBackground : themeColors.backgroundElement,
            borderColor: themeColors.border,
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
              <View style={[styles.accordionProgressBarTrack, { backgroundColor: themeColors.disabled }]}>
                <View
                  style={[
                    styles.accordionProgressBarFill,
                    { width: `${progressPercent}%`, backgroundColor: themeColors.emerald },
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
              tintColor={themeColors.emerald}
            />
          </View>
        </View>
      </TouchableOpacity>
    );
  };

  // Render Saved Layout Grid Matrix
  const renderLayoutGrid = () => {
    const positionedPlants = plants.filter(
      (p) => p.bed_x !== null && p.bed_y !== null && p.bed_x !== undefined && p.bed_y !== undefined
    );

    if (positionedPlants.length === 0) {
      return (
        <ThemedView type="backgroundElement" style={styles.emptyGridCard}>
          <SymbolView name="grid" size={32} tintColor={themeColors.placeholder} />
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
                    plant
                      ? { backgroundColor: themeColors.badgeSuccessBackground, borderWidth: 1.5, borderColor: themeColors.emerald }
                      : { backgroundColor: themeColors.backgroundElement, borderWidth: 1, borderColor: themeColors.border },
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
        <ActivityIndicator size="large" color={themeColors.emerald} />
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
            <TouchableOpacity onPress={refreshAll} style={[styles.refreshButton, { backgroundColor: themeColors.badgeSuccessBackground }]}>
              <SymbolView name="arrow.clockwise" size={20} tintColor={themeColors.emerald} />
            </TouchableOpacity>
          </View>

          {/* Quick Metrics Grid */}
          <View style={styles.metricsGrid}>
            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="leaf" size={24} tintColor={themeColors.emerald} />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {plants.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Plants
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="mappin.and.ellipse" size={24} tintColor={themeColors.blue} />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {locations.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Locations
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="drop.fill" size={24} tintColor={themeColors.cyan} />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {dueCrops.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Needs Water
              </ThemedText>
            </ThemedView>

            <ThemedView type="backgroundElement" style={styles.metricCard}>
              <SymbolView name="bell.badge.fill" size={24} tintColor={themeColors.badgeErrorText} />
              <ThemedText type="subtitle" style={styles.metricValue}>
                {unreadAlerts.length}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.metricLabel}>
                Alerts
              </ThemedText>
            </ThemedView>
          </View>

          {/* Accordion Item 1: Watering Queue */}
          <View style={styles.section}>
            {renderAccordionHeader(
              'watering',
              'Watering Queue',
              `Due: ${dueCrops.length} pending`,
              finishedWaterTasks,
              totalWaterTasks,
              waterProgress
            )}

            {expandedSection === 'watering' && (
              <View style={styles.accordionContentContainer}>
                {dueCrops.length === 0 ? (
                  <ThemedView type="backgroundElement" style={styles.emptyCard}>
                    <SymbolView name="checkmark.circle.fill" size={24} tintColor={themeColors.emerald} />
                    <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                      All plants are hydrated. No due tasks!
                    </ThemedText>
                  </ThemedView>
                ) : (
                  dueCrops.slice(0, 6).map((item, index) => {
                    const plantId = item.plant_id ?? item.id;
                    return (
                      <ThemedView
                        key={`due-${plantId ?? index}`}
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
                          style={[styles.waterButton, { backgroundColor: themeColors.careWater }]}
                          onPress={() => waterOne(plantId)}
                        >
                          <SymbolView name="drop.fill" size={14} tintColor={themeColors.textInverse} />
                          <ThemedText style={[styles.waterButtonText, { color: themeColors.textInverse }]}>Water</ThemedText>
                        </TouchableOpacity>
                      </ThemedView>
                    );
                  })
                )}
              </View>
            )}
          </View>

          {/* Accordion Item 2: Recent Notifications */}
          <View style={styles.section}>
            {renderAccordionHeader(
              'notifications',
              'Recent Notifications',
              `Alerts: ${unreadAlerts.length} unread`,
              readNotis,
              totalNotis,
              notiProgress
            )}

            {expandedSection === 'notifications' && (
              <View style={styles.accordionContentContainer}>
                {notifications.length === 0 ? (
                  <ThemedView type="backgroundElement" style={styles.emptyCard}>
                    <SymbolView name="envelope.open.fill" size={24} tintColor={themeColors.placeholder} />
                    <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                      No notifications.
                    </ThemedText>
                  </ThemedView>
                ) : (
                  notifications.slice(0, 5).map((noti) => (
                    <ThemedView
                      key={`noti-${noti.id}`}
                      type="backgroundElement"
                      style={[styles.notiItem, !noti.is_read && { borderLeftWidth: 4, borderLeftColor: themeColors.badgeErrorText }]}
                    >
                      <View style={styles.notiHeaderLine}>
                        <ThemedText type="smallBold" style={{ flex: 1 }}>
                          {noti.message}
                        </ThemedText>
                        <View style={[styles.statusBadge, noti.is_read ? { backgroundColor: themeColors.disabled } : { backgroundColor: themeColors.badgeErrorBackground }]}>
                          <ThemedText style={[styles.statusBadgeText, { color: noti.is_read ? themeColors.textSecondary : themeColors.badgeErrorText }]}>
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
            )}
          </View>

          {/* Accordion Item 3: Saved Layout */}
          <View style={styles.section}>
            {renderAccordionHeader(
              'layout',
              'Saved Bed Layout',
              `Placed: ${positionedPlantsCount}`,
              positionedPlantsCount,
              totalPlantsCount,
              layoutProgress
            )}

            {expandedSection === 'layout' && (
              <View style={styles.accordionContentContainer}>
                {renderLayoutGrid()}
              </View>
            )}
          </View>

          {/* Accordion Item 4: Farm Weather & Vitals */}
          <View style={styles.section}>
            {renderAccordionHeader(
              'weather',
              'Farm Weather & Vitals',
              weather ? `${weather.temperature}°C · ${weather.condition}` : 'Forecast ready',
              weather ? 1 : 0,
              1,
              weather ? 1 : 0
            )}

            {expandedSection === 'weather' && (
              <View style={styles.accordionContentContainer}>
                <ThemedView type="backgroundElement" style={styles.weatherCard}>
                  <View style={styles.weatherHeaderRow}>
                    <View style={{ flexDirection: 'row', alignItems: 'center', gap: Spacing.two, flex: 1 }}>
                      <SymbolView
                        name={weather ? (weather.iconName as any) : 'cloud.sun.fill'}
                        size={28}
                        tintColor={themeColors.primary}
                      />
                      <View style={{ flex: 1 }}>
                        <ThemedText type="smallBold">Farm Weather & Vitals</ThemedText>
                        <ThemedText themeColor="textSecondary" style={{ fontSize: 12 }}>
                          {weather ? `${weather.locationName} • ${weather.updatedAt}` : 'Real-time Forecast'}
                        </ThemedText>
                      </View>
                    </View>

                    <TouchableOpacity
                      style={[styles.fetchWeatherBtn, { backgroundColor: themeColors.primary }, weatherLoading && { opacity: 0.7 }]}
                      onPress={handleFetchWeather}
                      disabled={weatherLoading}
                    >
                      {weatherLoading ? (
                        <ActivityIndicator size="small" color={themeColors.textInverse} />
                      ) : (
                        <>
                          <SymbolView name={weather ? 'arrow.clockwise' : 'cloud.sun.fill'} size={14} tintColor={themeColors.textInverse} />
                          <ThemedText style={[styles.fetchWeatherBtnText, { color: themeColors.textInverse }]}>
                            {weather ? 'Refresh' : 'Fetch Weather'}
                          </ThemedText>
                        </>
                      )}
                    </TouchableOpacity>
                  </View>

                  {weatherError && (
                    <View style={styles.weatherErrorBox}>
                      <ThemedText style={styles.weatherErrorText}>{weatherError}</ThemedText>
                    </View>
                  )}

                  {weather ? (
                    <View style={{ marginTop: Spacing.two }}>
                      <View style={styles.weatherGrid}>
                        <View style={styles.weatherStatItem}>
                          <ThemedText type="subtitle" style={{ color: themeColors.primary, fontWeight: '700' }}>
                            {weather.temperature}°C
                          </ThemedText>
                          <ThemedText themeColor="textSecondary" style={styles.weatherStatLabel}>
                            {weather.condition}
                          </ThemedText>
                        </View>

                        <View style={styles.weatherStatItem}>
                          <ThemedText type="smallBold">
                            {weather.highTemp !== undefined ? `${weather.highTemp}° / ${weather.lowTemp}°` : '--'}
                          </ThemedText>
                          <ThemedText themeColor="textSecondary" style={styles.weatherStatLabel}>
                            High / Low
                          </ThemedText>
                        </View>

                        <View style={styles.weatherStatItem}>
                          <ThemedText type="smallBold">{weather.windspeed} km/h</ThemedText>
                          <ThemedText themeColor="textSecondary" style={styles.weatherStatLabel}>
                            Wind Speed
                          </ThemedText>
                        </View>
                      </View>

                      <View style={[styles.adviceBox, { backgroundColor: themeColors.surfaceSubtle }]}>
                        <SymbolView name="lightbulb.fill" size={16} tintColor={themeColors.primary} />
                        <ThemedText style={styles.adviceText}>{weather.farmingAdvice}</ThemedText>
                      </View>
                    </View>
                  ) : !weatherLoading ? (
                    <ThemedText themeColor="textSecondary" style={styles.weatherPromptText}>
                      Tap "Fetch Weather" to load current weather conditions and smart irrigation advice.
                    </ThemedText>
                  ) : null}
                </ThemedView>
              </View>
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
  weatherCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
  },
  weatherHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: Spacing.two,
  },
  fetchWeatherBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.one,
  },
  fetchWeatherBtnText: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
  },
  weatherPromptText: {
    marginTop: Spacing.two,
    fontSize: 13,
    lineHeight: 18,
  },
  weatherGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: Spacing.two,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: 'rgba(128, 128, 128, 0.15)',
    marginVertical: Spacing.two,
  },
  weatherStatItem: {
    alignItems: 'center',
  },
  weatherStatLabel: {
    fontSize: 11,
    marginTop: 2,
  },
  adviceBox: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    gap: Spacing.two,
  },
  adviceText: {
    fontSize: 12,
    flex: 1,
    fontWeight: '500',
  },
  weatherErrorBox: {
    backgroundColor: '#FEE2E2',
    padding: Spacing.two,
    borderRadius: Spacing.one,
    marginTop: Spacing.two,
  },
  weatherErrorText: {
    color: '#EF4444',
    fontSize: 12,
  },
  accordionHeaderCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: Spacing.three,
    backgroundColor: 'rgba(0, 0, 0, 0.03)',
    borderRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(128, 128, 128, 0.15)',
  },
  accordionHeaderCardActive: {
    borderBottomLeftRadius: 0,
    borderBottomRightRadius: 0,
    borderBottomWidth: 0,
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
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
  accordionContentContainer: {
    paddingTop: Spacing.two,
    paddingHorizontal: Spacing.two,
    paddingBottom: Spacing.two,
    borderBottomLeftRadius: Spacing.three,
    borderBottomRightRadius: Spacing.three,
    borderWidth: 1,
    borderColor: 'rgba(128, 128, 128, 0.15)',
    borderTopWidth: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.01)',
  },
});

