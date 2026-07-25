import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Modal,
  Alert,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import * as Location from 'expo-location';
import { useData } from '@/context/DataContext';
import { useAuth } from '@/context/AuthContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';
import { getApiBaseUrl, setApiBaseUrl } from '@/services/api';

const PLANT_TYPES = ["vegetable", "fruit", "flower", "herb", "evergreen", "succulent", "spice", "onion"];
const ENVIRONMENT_TYPES = ["outdoor", "indoor", "greenhouse"];

export default function MoreScreen() {
  const { logout, email } = useAuth();
  const {
    locations,
    recommendations,
    runRecommendations,
    clearRecommendations,
    addLocation,
    editLocation,
    removeLocation,
    addPlant,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const [activeSegment, setActiveSegment] = useState<'locations' | 'recommendations' | 'settings'>('locations');
  const [actionLoading, setActionLoading] = useState(false);
  const [recsLoading, setRecsLoading] = useState(false);

  // Dynamic API URL state
  const [apiUrl, setApiUrl] = useState('');

  // Location Form states
  const [addLocVisible, setAddLocVisible] = useState(false);
  const [editLocVisible, setEditLocVisible] = useState(false);
  const [selectedLoc, setSelectedLoc] = useState<any>(null);

  // New Location Fields
  const [locName, setLocName] = useState('');
  const [locDesc, setLocDesc] = useState('');
  const [locEnv, setLocEnv] = useState('outdoor');
  const [locWidth, setLocWidth] = useState('5.0');
  const [locLength, setLocLength] = useState('5.0');
  const [locLat, setLocLat] = useState('');
  const [locLng, setLocLng] = useState('');

  // Edit Location Fields
  const [editLocName, setEditLocName] = useState('');
  const [editLocDesc, setEditLocDesc] = useState('');
  const [editLocEnv, setEditLocEnv] = useState('outdoor');
  const [editLocWidth, setEditLocWidth] = useState('5.0');
  const [editLocLength, setEditLocLength] = useState('5.0');
  const [editLocLat, setEditLocLat] = useState('');
  const [editLocLng, setEditLocLng] = useState('');

  const [gpsLoading, setGpsLoading] = useState(false);

  // Recommendation additions state
  const [selectedAddType, setSelectedAddType] = useState('vegetable');
  const [selectedAddLocId, setSelectedAddLocId] = useState<number | null>(null);
  const [selectedRecCrops, setSelectedRecCrops] = useState<string[]>([]);

  useEffect(() => {
    async function loadUrl() {
      const url = await getApiBaseUrl();
      setApiUrl(url);
    }
    loadUrl();
  }, []);

  useEffect(() => {
    if (locations.length > 0 && selectedAddLocId === null) {
      setSelectedAddLocId(locations[0].id);
    }
  }, [locations]);

  const handleFetchCurrentLocation = async (isEdit: boolean) => {
    setGpsLoading(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission Denied', 'Permission to access location was denied. Please enable location services in your system settings.');
        return;
      }

      const pos = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });

      if (pos && pos.coords) {
        const latStr = String(pos.coords.latitude.toFixed(6));
        const lngStr = String(pos.coords.longitude.toFixed(6));
        if (isEdit) {
          setEditLocLat(latStr);
          setEditLocLng(lngStr);
        } else {
          setLocLat(latStr);
          setLocLng(lngStr);
        }
      }
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to fetch device GPS location');
    } finally {
      setGpsLoading(false);
    }
  };

  const handleCreateLocation = async () => {
    if (!locName.trim()) {
      Alert.alert('Error', 'Location name is required');
      return;
    }
    setActionLoading(true);
    try {
      await addLocation({
        name: locName.trim(),
        description: locDesc.trim() || null,
        environment_type: locEnv,
        width_m: parseFloat(locWidth) || 5.0,
        length_m: parseFloat(locLength) || 5.0,
        latitude: parseFloat(locLat) || null,
        longitude: parseFloat(locLng) || null,
      });
      setAddLocVisible(false);
      setLocName('');
      setLocDesc('');
      setLocLat('');
      setLocLng('');
      Alert.alert('Success', 'Location created successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to create location');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateLocation = async () => {
    if (!editLocName.trim()) {
      Alert.alert('Error', 'Location name is required');
      return;
    }
    setActionLoading(true);
    try {
      await editLocation(selectedLoc.id, {
        name: editLocName.trim(),
        description: editLocDesc.trim() || null,
        environment_type: editLocEnv,
        width_m: parseFloat(editLocWidth) || 5.0,
        length_m: parseFloat(editLocLength) || 5.0,
        latitude: parseFloat(editLocLat) || null,
        longitude: parseFloat(editLocLng) || null,
      });
      setEditLocVisible(false);
      Alert.alert('Success', 'Location updated successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to update location');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteLoc = (locId: number, name: string) => {
    const message = `Are you sure you want to delete "${name}"? All plants in this location will lose their location ID.`;

    if (Platform.OS === 'web') {
      const confirmDelete = window.confirm(message);
      if (confirmDelete) {
        (async () => {
          try {
            await removeLocation(locId);
            setEditLocVisible(false);
          } catch (e: any) {
            alert(e.message || 'Failed to delete location');
          }
        })();
      }
      return;
    }

    Alert.alert(
      'Confirm Delete',
      message,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await removeLocation(locId);
              setEditLocVisible(false);
            } catch (e: any) {
              Alert.alert('Error', e.message || 'Failed to delete location');
            }
          },
        },
      ]
    );
  };

  const openEditLoc = (loc: any) => {
    setSelectedLoc(loc);
    setEditLocName(loc.name || '');
    setEditLocDesc(loc.description || '');
    setEditLocEnv(loc.environment_type || 'outdoor');
    setEditLocWidth(String(loc.width_m || 5.0));
    setEditLocLength(String(loc.length_m || 5.0));
    setEditLocLat(loc.latitude ? String(loc.latitude) : '');
    setEditLocLng(loc.longitude ? String(loc.longitude) : '');
    setEditLocVisible(true);
  };

  const handleSaveApiUrl = async () => {
    if (!apiUrl.trim()) return;
    try {
      await setApiBaseUrl(apiUrl.trim());
      Alert.alert('Success', 'API URL updated successfully. Please reload or sign in again if endpoints disconnect.');
    } catch (e) {
      Alert.alert('Error', 'Failed to update API URL');
    }
  };

  const handleRunRecs = async () => {
    setRecsLoading(true);
    try {
      await runRecommendations();
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to generate recommendations');
    } finally {
      setRecsLoading(false);
    }
  };

  const toggleRecCropSelection = (cropName: string) => {
    if (selectedRecCrops.includes(cropName)) {
      setSelectedRecCrops(selectedRecCrops.filter((x) => x !== cropName));
    } else {
      setSelectedRecCrops([...selectedRecCrops, cropName]);
    }
  };

  const handleAddSelectedRecs = async () => {
    if (selectedRecCrops.length === 0 || selectedAddLocId === null) return;
    setActionLoading(true);
    const added: string[] = [];
    const errors: string[] = [];

    for (const crop of selectedRecCrops) {
      try {
        await addPlant({
          name: crop.replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
          plant_type: selectedAddType,
          location_id: selectedAddLocId,
          use_sensor: false,
        });
        added.push(crop);
      } catch (e: any) {
        errors.push(`${crop}: ${e.message}`);
      }
    }

    setActionLoading(false);
    setSelectedRecCrops([]);
    clearRecommendations(); // clear old recommendations so user runs again

    if (added.length > 0) {
      Alert.alert('Success', `Added ${added.length} plant(s): ${added.join(', ')}`);
    }
    if (errors.length > 0) {
      Alert.alert('Errors Encountered', errors.join('\n'));
    }
  };

  // Process companion lists
  const interactions = recommendations?.existing_plant_interactions || {};
  const newSuggestions = recommendations?.new_companion_suggestions || {};
  const goodSuggestions = newSuggestions.suggest_good || {};
  const badSuggestions = newSuggestions.suggest_bad || {};

  // Aggregate ranked companion additions
  const getRankedAdditions = () => {
    const list: any[] = [];
    const seen = new Set<string>();

    Object.entries(goodSuggestions).forEach(([_, itemArray]: any) => {
      itemArray.forEach((item: any) => {
        const name = item.plant;
        if (!name || seen.has(name)) return;
        seen.add(name);
        list.push(item);
      });
    });
    return list.slice(0, 10); // show top 10
  };

  const rankedAdditions = getRankedAdditions();

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <ThemedText type="subtitle" style={styles.title}>
              Farm Settings
            </ThemedText>
            <ThemedText themeColor="textSecondary">
              Locations, companion rules, and profile
            </ThemedText>
          </View>
          <View style={styles.headerActions}>
            {activeSegment === 'locations' && (
              <TouchableOpacity
                style={styles.addButton}
                onPress={() => setAddLocVisible(true)}
              >
                <SymbolView name="plus" size={16} tintColor="#fff" />
                <ThemedText style={styles.addButtonText}>Add Location</ThemedText>
              </TouchableOpacity>
            )}
            <TouchableOpacity
              accessibilityLabel="Sign out"
              style={styles.headerLogoutBtn}
              onPress={logout}
            >
              <SymbolView name="rectangle.portrait.and.arrow.right" size={18} tintColor="#fff" />
            </TouchableOpacity>
          </View>
        </View>

        {/* Segment selector */}
        <View style={styles.segmentedContainer}>
          <TouchableOpacity
            style={[styles.segmentBtn, activeSegment === 'locations' && styles.segmentBtnActive]}
            onPress={() => setActiveSegment('locations')}
          >
            <ThemedText style={[styles.segmentText, activeSegment === 'locations' && styles.segmentTextActive]}>
              Locations
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segmentBtn, activeSegment === 'recommendations' && styles.segmentBtnActive]}
            onPress={() => setActiveSegment('recommendations')}
          >
            <ThemedText style={[styles.segmentText, activeSegment === 'recommendations' && styles.segmentTextActive]}>
              Companions
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.segmentBtn, activeSegment === 'settings' && styles.segmentBtnActive]}
            onPress={() => setActiveSegment('settings')}
          >
            <ThemedText style={[styles.segmentText, activeSegment === 'settings' && styles.segmentTextActive]}>
              Profile
            </ThemedText>
          </TouchableOpacity>
        </View>

        {/* Content list */}
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : activeSegment === 'locations' ? (
          <ScrollView
            contentContainerStyle={styles.scrollList}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {locations.length === 0 ? (
              <View style={styles.empty}>
                <SymbolView name="mappin.slash" size={48} tintColor="#ccc" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  No growing locations set up. Click '+' to add one!
                </ThemedText>
              </View>
            ) : (
              locations.map((loc) => (
                <ThemedView key={loc.id} type="backgroundElement" style={styles.card}>
                  <View style={styles.cardHeader}>
                    <TouchableOpacity onPress={() => openEditLoc(loc)} style={{ flex: 1 }}>
                      <ThemedText type="smallBold" style={styles.locNameText}>
                        {loc.name}
                      </ThemedText>
                      <ThemedText themeColor="textSecondary" style={styles.locDescText}>
                        {loc.description || 'No description provided'}
                      </ThemedText>
                    </TouchableOpacity>
                    <TouchableOpacity onPress={() => openEditLoc(loc)} style={styles.editLocBtn}>
                      <SymbolView name="pencil" size={16} tintColor="#10B981" />
                    </TouchableOpacity>
                  </View>

                  <View style={styles.locDetailsGrid}>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Environment
                      </ThemedText>
                      <ThemedText type="smallBold">{loc.environment_type}</ThemedText>
                    </View>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Size
                      </ThemedText>
                      <ThemedText type="smallBold">
                        {loc.width_m} m x {loc.length_m} m
                      </ThemedText>
                    </View>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Area
                      </ThemedText>
                      <ThemedText type="smallBold">
                        {(Number(loc.width_m || 0) * Number(loc.length_m || 0)).toFixed(1)} m²
                      </ThemedText>
                    </View>
                  </View>
                  {loc.latitude !== null && loc.longitude !== null && loc.latitude !== undefined && loc.longitude !== undefined && (
                    <View style={styles.locGpsDisplay}>
                      <SymbolView name="location.fill" size={12} tintColor="#10B981" />
                      <ThemedText themeColor="textSecondary" style={styles.locGpsDisplayText}>
                        GPS: {Number(loc.latitude).toFixed(5)}, {Number(loc.longitude).toFixed(5)}
                      </ThemedText>
                    </View>
                  )}
                </ThemedView>
              ))
            )}
          </ScrollView>
        ) : activeSegment === 'recommendations' ? (
          /* COMPANION PLANTING SECTION */
          <ScrollView contentContainerStyle={styles.scrollList}>
            {!recommendations ? (
              <View style={styles.empty}>
                <SymbolView name="sparkles" size={48} tintColor="#ccc" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  Generate companion recommendations using Prolog rules analysis.
                </ThemedText>
                <TouchableOpacity
                  style={styles.runRecsBtn}
                  onPress={handleRunRecs}
                  disabled={recsLoading}
                >
                  {recsLoading ? (
                    <ActivityIndicator color="#fff" />
                  ) : (
                    <>
                      <SymbolView name="wand.and.stars" size={16} tintColor="#fff" />
                      <ThemedText style={styles.runRecsBtnText}>Generate Recommendations</ThemedText>
                    </>
                  )}
                </TouchableOpacity>
              </View>
            ) : (
              <View>
                {/* Header Controls for additions */}
                <ThemedView type="backgroundElement" style={styles.recsAddHeaderCard}>
                  <ThemedText type="smallBold" style={{ marginBottom: Spacing.two }}>
                    Highest Value Additions (Checked Additions)
                  </ThemedText>

                  <ThemedText style={styles.fieldLabel}>Type for added plants</ThemedText>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalSelectorScroll}>
                    {PLANT_TYPES.map((type) => (
                      <TouchableOpacity
                        key={type}
                        style={[
                          styles.smallTypeOption,
                          selectedAddType === type && styles.smallTypeOptionActive,
                        ]}
                        onPress={() => setSelectedAddType(type)}
                      >
                        <ThemedText style={[styles.smallTypeOptionText, selectedAddType === type && { color: '#fff' }]}>
                          {type}
                        </ThemedText>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>

                  <ThemedText style={styles.fieldLabel}>Location for added plants</ThemedText>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.horizontalSelectorScroll}>
                    {locations.map((loc) => (
                      <TouchableOpacity
                        key={loc.id}
                        style={[
                          styles.smallTypeOption,
                          selectedAddLocId === loc.id && styles.smallTypeOptionActive,
                        ]}
                        onPress={() => setSelectedAddLocId(loc.id)}
                      >
                        <ThemedText style={[styles.smallTypeOptionText, selectedAddLocId === loc.id && { color: '#fff' }]}>
                          {loc.name}
                        </ThemedText>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>

                  <TouchableOpacity
                    style={[styles.runRecsBtn, { alignSelf: 'stretch', marginTop: Spacing.three }]}
                    onPress={handleAddSelectedRecs}
                    disabled={selectedRecCrops.length === 0 || actionLoading}
                  >
                    <ThemedText style={styles.runRecsBtnText}>
                      Add Selected Plants ({selectedRecCrops.length})
                    </ThemedText>
                  </TouchableOpacity>

                  <TouchableOpacity
                    style={[styles.runRecsBtn, { alignSelf: 'stretch', marginTop: Spacing.two, backgroundColor: '#6B7280' }]}
                    onPress={clearRecommendations}
                  >
                    <ThemedText style={styles.runRecsBtnText}>Reset / Clear Analysis</ThemedText>
                  </TouchableOpacity>
                </ThemedView>

                {/* Ranked Additions List */}
                <ThemedText type="smallBold" style={styles.categoryTitle}>
                  Add Companion Suggestions
                </ThemedText>

                {rankedAdditions.length === 0 ? (
                  <ThemedText themeColor="textSecondary" style={{ marginBottom: Spacing.three }}>
                    No suggestions.
                  </ThemedText>
                ) : (
                  rankedAdditions.map((item: any) => {
                    const isChecked = selectedRecCrops.includes(item.plant);
                    return (
                      <ThemedView key={item.plant} type="backgroundElement" style={styles.recItemCard}>
                        <TouchableOpacity
                          style={styles.checkboxLine}
                          onPress={() => toggleRecCropSelection(item.plant)}
                        >
                          <SymbolView
                            name={isChecked ? 'checkmark.square.fill' : 'square'}
                            size={20}
                            tintColor={isChecked ? '#10B981' : '#888'}
                          />
                          <View style={{ flex: 1, marginLeft: Spacing.two }}>
                            <ThemedText type="smallBold">
                              {String(item.plant).replace('_', ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                            </ThemedText>
                            <ThemedText type="small" themeColor="textSecondary">
                              Supports: {item.supports?.join(', ')}
                            </ThemedText>
                            <ThemedText type="small" themeColor="textSecondary">
                              Confidence Score: {item.confidence?.toFixed(1) || item.average_score?.toFixed(1) || 'N/A'}
                            </ThemedText>
                          </View>
                        </TouchableOpacity>
                      </ThemedView>
                    );
                  })
                )}

                {/* Avoid Recommendations */}
                {Object.keys(badSuggestions).length > 0 && (
                  <>
                    <ThemedText type="smallBold" style={[styles.categoryTitle, { color: '#EF4444' }]}>
                      Avoid Adding
                    </ThemedText>
                    {Object.entries(badSuggestions).map(([pName, items]: any) => (
                      <ThemedView key={`avoid-${pName}`} type="backgroundElement" style={styles.recItemCard}>
                        <ThemedText type="smallBold">Near {pName}</ThemedText>
                        <ThemedText type="small" style={{ color: '#EF4444', marginTop: 2 }}>
                          Avoid: {items.map((i: any) => i.plant).join(', ')}
                        </ThemedText>
                      </ThemedView>
                    ))}
                  </>
                )}

                {/* Existing Plant Pairs Recommendations */}
                {interactions.recommended?.length > 0 && (
                  <>
                    <ThemedText type="smallBold" style={styles.categoryTitle}>
                      Existing Plant Pairs
                    </ThemedText>
                    {interactions.recommended.map((item: any, idx: number) => (
                      <ThemedView key={`pair-${idx}`} type="backgroundElement" style={styles.recItemCard}>
                        <ThemedText type="smallBold">{item.pair}</ThemedText>
                        <ThemedText type="small" themeColor="textSecondary">
                          {item.description || 'Recommended matching compatibilities.'}
                        </ThemedText>
                      </ThemedView>
                    ))}
                  </>
                )}
              </View>
            )}
          </ScrollView>
        ) : (
          /* PROFILE & CONFIGURATION SETTINGS SECTION */
          <ScrollView contentContainerStyle={styles.scrollList}>
            {/* User details */}
            <ThemedView type="backgroundElement" style={styles.profileCard}>
              <SymbolView name="person.crop.circle.fill" size={64} tintColor="#10B981" />
              <ThemedText type="subtitle" style={styles.profileEmail}>
                {email || 'Signed In User'}
              </ThemedText>
              <ThemedText themeColor="textSecondary" style={styles.profileSub}>
                Authorized Farmer
              </ThemedText>
            </ThemedView>

            {/* Target Server Config */}
            <ThemedView type="backgroundElement" style={styles.card}>
              <ThemedText type="smallBold" style={{ marginBottom: Spacing.two }}>
                API Connection Settings
              </ThemedText>
              <ThemedText type="small" themeColor="textSecondary" style={{ marginBottom: Spacing.two }}>
                Specify local server address. Falling back to default if empty.
              </ThemedText>
              <TextInput
                style={styles.input}
                value={apiUrl}
                onChangeText={setApiUrl}
                placeholder="http://10.0.2.2:8000"
                placeholderTextColor="#888"
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity style={styles.saveUrlBtn} onPress={handleSaveApiUrl}>
                <ThemedText style={{ color: '#fff', fontWeight: 'bold' }}>Save Server URL</ThemedText>
              </TouchableOpacity>
            </ThemedView>

            {/* Sign out */}
            <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
              <SymbolView name="rectangle.portrait.and.arrow.right" size={18} tintColor="#fff" />
              <ThemedText style={styles.logoutBtnText}>Sign Out from Farm</ThemedText>
            </TouchableOpacity>
          </ScrollView>
        )}
      </SafeAreaView>

      {/* Add Location Modal */}
      <Modal
        visible={addLocVisible}
        animationType="slide"
        onRequestClose={() => setAddLocVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle">Add Location</ThemedText>
            <TouchableOpacity onPress={() => setAddLocVisible(false)}>
              <SymbolView name="xmark" size={24} tintColor="#10B981" />
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Location Name *</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Balcony, Greenhouse shelf, Backyard"
              placeholderTextColor="#888"
              value={locName}
              onChangeText={setLocName}
            />

            <ThemedText style={styles.fieldLabel}>Description</ThemedText>
            <TextInput
              style={[styles.input, { height: 80, paddingTop: 10 }]}
              multiline
              numberOfLines={3}
              placeholder="e.g. Sunny east-facing balcony."
              placeholderTextColor="#888"
              value={locDesc}
              onChangeText={setLocDesc}
            />

            <ThemedText style={styles.fieldLabel}>Environment</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {ENVIRONMENT_TYPES.map((env) => (
                <TouchableOpacity
                  key={env}
                  style={[
                    styles.typeOption,
                    locEnv === env && styles.typeOptionSelected,
                  ]}
                  onPress={() => setLocEnv(env)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      locEnv === env && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {env}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Width (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={locWidth}
                  onChangeText={setLocWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={locLength}
                  onChangeText={setLocLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Latitude (optional)</ThemedText>
                <TextInput
                  style={styles.input}
                  placeholder="e.g. 37.7749"
                  placeholderTextColor="#888"
                  value={locLat}
                  onChangeText={setLocLat}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Longitude (optional)</ThemedText>
                <TextInput
                  style={styles.input}
                  placeholder="e.g. -122.4194"
                  placeholderTextColor="#888"
                  value={locLng}
                  onChangeText={setLocLng}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <TouchableOpacity
              style={styles.gpsBtn}
              onPress={() => handleFetchCurrentLocation(false)}
              disabled={gpsLoading}
            >
              {gpsLoading ? (
                <ActivityIndicator color="#10B981" />
              ) : (
                <>
                  <SymbolView name="location.fill" size={16} tintColor="#10B981" />
                  <ThemedText style={styles.gpsBtnText}>Use Current Location (GPS)</ThemedText>
                </>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handleCreateLocation}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <ThemedText style={styles.submitBtnText}>Create Location</ThemedText>
              )}
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Location Modal */}
      <Modal
        visible={editLocVisible}
        animationType="slide"
        onRequestClose={() => setEditLocVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle">Edit Location</ThemedText>
            <TouchableOpacity onPress={() => setEditLocVisible(false)}>
              <SymbolView name="xmark" size={24} tintColor="#10B981" />
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Location Name *</ThemedText>
            <TextInput
              style={styles.input}
              value={editLocName}
              onChangeText={setEditLocName}
            />

            <ThemedText style={styles.fieldLabel}>Description</ThemedText>
            <TextInput
              style={[styles.input, { height: 80, paddingTop: 10 }]}
              multiline
              numberOfLines={3}
              value={editLocDesc}
              onChangeText={setEditLocDesc}
            />

            <ThemedText style={styles.fieldLabel}>Environment</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {ENVIRONMENT_TYPES.map((env) => (
                <TouchableOpacity
                  key={env}
                  style={[
                    styles.typeOption,
                    editLocEnv === env && styles.typeOptionSelected,
                  ]}
                  onPress={() => setEditLocEnv(env)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      editLocEnv === env && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {env}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Width (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={editLocWidth}
                  onChangeText={setEditLocWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={editLocLength}
                  onChangeText={setEditLocLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Latitude (optional)</ThemedText>
                <TextInput
                  style={styles.input}
                  placeholder="e.g. 37.7749"
                  placeholderTextColor="#888"
                  value={editLocLat}
                  onChangeText={setEditLocLat}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Longitude (optional)</ThemedText>
                <TextInput
                  style={styles.input}
                  placeholder="e.g. -122.4194"
                  placeholderTextColor="#888"
                  value={editLocLng}
                  onChangeText={setEditLocLng}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <TouchableOpacity
              style={styles.gpsBtn}
              onPress={() => handleFetchCurrentLocation(true)}
              disabled={gpsLoading}
            >
              {gpsLoading ? (
                <ActivityIndicator color="#10B981" />
              ) : (
                <>
                  <SymbolView name="location.fill" size={16} tintColor="#10B981" />
                  <ThemedText style={styles.gpsBtnText}>Use Current Location (GPS)</ThemedText>
                </>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handleUpdateLocation}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <ThemedText style={styles.submitBtnText}>Save Changes</ThemedText>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.submitBtn, styles.deleteBtn]}
              onPress={() => handleDeleteLoc(selectedLoc.id, selectedLoc.name)}
              disabled={actionLoading}
            >
              <ThemedText style={styles.submitBtnText}>Delete Location</ThemedText>
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>
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
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.two,
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#10B981',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.one,
  },
  addButtonText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  headerLogoutBtn: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#EF4444',
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
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: Spacing.two,
    borderRadius: Spacing.two,
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
  scrollList: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
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
    marginBottom: Spacing.four,
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.three,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.two,
    gap: Spacing.two,
  },
  locNameText: {
    fontSize: 16,
  },
  locDescText: {
    fontSize: 12,
    marginTop: 2,
  },
  editLocBtn: {
    padding: Spacing.one,
  },
  locDetailsGrid: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.02)',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginTop: Spacing.two,
  },
  detailBox: {
    flex: 1,
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 10,
    marginBottom: 2,
  },
  runRecsBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#10B981',
    paddingVertical: Spacing.three,
    paddingHorizontal: Spacing.four,
    borderRadius: Spacing.two,
    gap: Spacing.two,
  },
  runRecsBtnText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  recsAddHeaderCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.four,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: Spacing.two,
    marginBottom: Spacing.one,
  },
  horizontalSelectorScroll: {
    flexDirection: 'row',
    marginBottom: Spacing.one,
  },
  smallTypeOption: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 12,
    backgroundColor: '#e5e7eb',
    marginRight: 6,
  },
  smallTypeOptionActive: {
    backgroundColor: '#10B981',
  },
  smallTypeOptionText: {
    fontSize: 11,
    color: '#374151',
  },
  categoryTitle: {
    fontSize: 16,
    marginBottom: Spacing.two,
    marginTop: Spacing.two,
  },
  recItemCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.two,
  },
  checkboxLine: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  profileCard: {
    padding: Spacing.five,
    borderRadius: Spacing.three,
    alignItems: 'center',
    marginBottom: Spacing.four,
  },
  profileEmail: {
    fontWeight: 'bold',
    marginTop: Spacing.two,
  },
  profileSub: {
    fontSize: 12,
    marginTop: 2,
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: Spacing.two,
    paddingHorizontal: Spacing.three,
    marginBottom: Spacing.two,
    fontSize: 16,
    color: '#000',
    backgroundColor: '#f9f9f9',
  },
  saveUrlBtn: {
    backgroundColor: '#10B981',
    paddingVertical: Spacing.two,
    alignItems: 'center',
    borderRadius: Spacing.one,
    marginTop: Spacing.one,
  },
  logoutBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#EF4444',
    paddingVertical: Spacing.three,
    borderRadius: Spacing.two,
    marginTop: Spacing.two,
    gap: Spacing.two,
  },
  logoutBtnText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 15,
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.four,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  modalForm: {
    padding: Spacing.four,
  },
  horizontalSelect: {
    flexDirection: 'row',
    paddingVertical: Spacing.one,
    gap: Spacing.two,
    marginBottom: Spacing.two,
  },
  typeOption: {
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ccc',
  },
  typeOptionSelected: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
  },
  typeOptionText: {
    fontSize: 14,
    color: '#333',
  },
  formRow: {
    flexDirection: 'row',
  },
  submitBtn: {
    height: 48,
    backgroundColor: '#10B981',
    borderRadius: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.five,
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  deleteBtn: {
    backgroundColor: '#ba3434',
    marginTop: Spacing.two,
  },
  gpsBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: '#10B981',
    borderRadius: Spacing.two,
    paddingVertical: Spacing.two,
    marginTop: Spacing.two,
    marginBottom: Spacing.one,
    gap: Spacing.two,
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
  },
  gpsBtnText: {
    color: '#10B981',
    fontWeight: 'bold',
    fontSize: 14,
  },
  locGpsDisplay: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.two,
    gap: Spacing.one,
    backgroundColor: 'rgba(16, 185, 129, 0.05)',
    paddingVertical: 4,
    paddingHorizontal: Spacing.two,
    borderRadius: Spacing.one,
    alignSelf: 'flex-start',
  },
  locGpsDisplayText: {
    fontSize: 11,
    color: '#10B981',
    fontWeight: '600',
  },
});
