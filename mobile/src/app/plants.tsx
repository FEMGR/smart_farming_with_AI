import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Modal,
  Switch,
  Alert,
  RefreshControl,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useRouter } from 'expo-router';
import { useData } from '@/context/DataContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';

const PLANT_TYPES = ["vegetable", "fruit", "flower", "herb", "evergreen", "succulent", "spice", "onion"];

export default function PlantsScreen() {
  const router = useRouter();
  const {
    plants,
    locations,
    addPlant,
    editPlant,
    removePlant,
    dupPlant,
    waterOne,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const [searchQuery, setSearchQuery] = useState('');
  
  // Forms states
  const [addModalVisible, setAddModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [selectedPlant, setSelectedPlant] = useState<any>(null);
  
  // New Plant Form State
  const [name, setName] = useState('');
  const [speciesName, setSpeciesName] = useState('');
  const [plantType, setPlantType] = useState('vegetable');
  const [locationId, setLocationId] = useState<number | null>(null);
  const [useSensor, setUseSensor] = useState(false);
  const [wateringInterval, setWateringInterval] = useState('0');
  const [speciesId, setSpeciesId] = useState('0');

  // Edit Plant Form State
  const [editName, setEditName] = useState('');
  const [editSpeciesName, setEditSpeciesName] = useState('');
  const [editPlantType, setEditPlantType] = useState('vegetable');
  const [editLocationId, setEditLocationId] = useState<number | null>(null);
  const [editUseSensor, setEditUseSensor] = useState(false);
  const [editWateringInterval, setEditWateringInterval] = useState('0');

  const [formLoading, setFormLoading] = useState(false);

  // Set initial location on mount or when locations load
  React.useEffect(() => {
    if (locations.length > 0 && locationId === null) {
      setLocationId(locations[0].id);
    }
  }, [locations]);

  const handleCreatePlant = async () => {
    if (!name.trim()) {
      Alert.alert('Validation Error', 'Plant name is required');
      return;
    }

    setFormLoading(true);
    try {
      const payload: any = {
        name: name.trim(),
        plant_type: plantType,
        species_name: speciesName.trim() || null,
        location_id: locationId,
        use_sensor: useSensor,
        watering_interval_days: parseInt(wateringInterval) || null,
      };

      const sId = parseInt(speciesId) || 0;
      await addPlant(payload, sId > 0 ? sId : undefined);
      
      // Reset form
      setName('');
      setSpeciesName('');
      setPlantType('vegetable');
      setUseSensor(false);
      setWateringInterval('0');
      setSpeciesId('0');
      setAddModalVisible(false);
      
      Alert.alert('Success', 'Plant added successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to add plant');
    } finally {
      setFormLoading(false);
    }
  };

  const handleUpdatePlant = async () => {
    if (!editName.trim()) {
      Alert.alert('Validation Error', 'Plant name is required');
      return;
    }

    setFormLoading(true);
    try {
      const payload: any = {
        name: editName.trim(),
        plant_type: editPlantType,
        species_name: editSpeciesName.trim() || null,
        location_id: editLocationId,
        use_sensor: editUseSensor,
        watering_interval_days: parseInt(editWateringInterval) || null,
      };

      await editPlant(selectedPlant.id, payload);
      setEditModalVisible(false);
      Alert.alert('Success', 'Plant updated successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to update plant');
    } finally {
      setFormLoading(false);
    }
  };

  const deletePlantById = async (plantId: number) => {
    setFormLoading(true);
    try {
      await removePlant(plantId);
      setEditModalVisible(false);
      setSelectedPlant(null);
    } catch (e: any) {
      if (Platform.OS === 'web') {
        window.alert(e.message || 'Failed to delete plant');
      } else {
        Alert.alert('Error', e.message || 'Failed to delete plant');
      }
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeletePlant = (plantId: number, plantName: string) => {
    const message = `Are you sure you want to delete "${plantName}"?`;

    if (Platform.OS === 'web') {
      if (window.confirm(message)) {
        deletePlantById(plantId);
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
          onPress: () => deletePlantById(plantId),
        },
      ]
    );
  };

  const openEditModal = (plant: any) => {
    setSelectedPlant(plant);
    setEditName(plant.name || '');
    setEditSpeciesName(plant.scientific_name || '');
    setEditPlantType(plant.plant_type || 'vegetable');
    setEditLocationId(plant.location_id || (locations[0]?.id || null));
    setEditUseSensor(!!plant.use_sensor);
    setEditWateringInterval(String(plant.watering_interval_days || 0));
    setEditModalVisible(true);
  };

  const handleDuplicate = async (plantId: number) => {
    try {
      await dupPlant(plantId);
      Alert.alert('Success', 'Plant duplicated successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to duplicate plant');
    }
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return 'Never';
    try {
      return new Date(dateStr).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const filteredPlants = plants.filter((plant) => {
    const query = searchQuery.toLowerCase();
    const nameMatch = (plant.name || '').toLowerCase().includes(query);
    const scientificMatch = (plant.scientific_name || '').toLowerCase().includes(query);
    const typeMatch = (plant.plant_type || '').toLowerCase().includes(query);
    return nameMatch || scientificMatch || typeMatch;
  });

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <ThemedText type="subtitle" style={styles.title}>
              Plants
            </ThemedText>
            <ThemedText themeColor="textSecondary">
              Manage and track your plant varieties
            </ThemedText>
          </View>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setAddModalVisible(true)}
          >
            <SymbolView name="plus" size={16} tintColor="#fff" />
            <ThemedText style={styles.addButtonText}>Add Plant</ThemedText>
          </TouchableOpacity>
        </View>

        {/* Search */}
        <View style={styles.searchContainer}>
          <SymbolView name="magnifyingglass" size={18} tintColor="#888" style={styles.searchIcon} />
          <TextInput
            style={styles.searchInput}
            placeholder="Search by name, type, scientific name..."
            placeholderTextColor="#888"
            value={searchQuery}
            onChangeText={setSearchQuery}
            autoCapitalize="none"
          />
        </View>

        {/* Plants List */}
        {loading && plants.length === 0 ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : filteredPlants.length === 0 ? (
          <ScrollView
            contentContainerStyle={styles.emptyContainer}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            <SymbolView name="leaf.fill" size={48} tintColor="#ccc" />
            <ThemedText themeColor="textSecondary" style={styles.emptyText}>
              No plants found. Try adding a new plant!
            </ThemedText>
          </ScrollView>
        ) : (
          <ScrollView
            contentContainerStyle={styles.listContainer}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {filteredPlants.map((plant) => {
              const location = locations.find((l) => l.id === plant.location_id);
              const timeline = plant.timeline_snapshot || {};
              const events = timeline.events || [];
              const warnings = timeline.warnings || [];

              return (
                <ThemedView key={plant.id} type="backgroundElement" style={styles.plantCard}>
                  {/* Title & Badges */}
                  <View style={styles.plantHeader}>
                    <View style={{ flex: 1 }}>
                      <ThemedText type="smallBold" style={styles.plantName}>
                        {plant.name}
                      </ThemedText>
                      <ThemedText themeColor="textSecondary" style={styles.plantSciName}>
                        {plant.scientific_name || 'No scientific name'}
                      </ThemedText>
                    </View>
                    <View style={styles.badgeContainer}>
                      <View style={styles.typeBadge}>
                        <ThemedText style={styles.badgeText}>{plant.plant_type}</ThemedText>
                      </View>
                      <View style={styles.locBadge}>
                        <ThemedText style={styles.badgeText}>{location?.name || 'No Location'}</ThemedText>
                      </View>
                    </View>
                  </View>

                  {/* Metadata Row */}
                  <View style={styles.metadataRow}>
                    <View style={styles.metaItem}>
                      <ThemedText themeColor="textSecondary" style={styles.metaLabel}>
                        Water Interval
                      </ThemedText>
                      <ThemedText type="smallBold">
                        {plant.effective_watering_interval || plant.watering_interval_days || 4} days
                      </ThemedText>
                    </View>
                    <View style={styles.metaItem}>
                      <ThemedText themeColor="textSecondary" style={styles.metaLabel}>
                        Last Watered
                      </ThemedText>
                      <ThemedText type="smallBold">{formatDate(plant.last_watered)}</ThemedText>
                    </View>
                    <View style={styles.metaItem}>
                      <ThemedText themeColor="textSecondary" style={styles.metaLabel}>
                        Source
                      </ThemedText>
                      <ThemedText type="smallBold">{plant.data_source || 'manual'}</ThemedText>
                    </View>
                  </View>

                  {/* Taxonomy info */}
                  {(plant.genus || plant.plant_atom) && (
                    <View style={styles.taxonomyRow}>
                      <ThemedText style={styles.taxonomyText} themeColor="textSecondary">
                        Atom: {plant.plant_atom || '-'} · Genus: {plant.genus || '-'}
                      </ThemedText>
                    </View>
                  )}

                  {/* Timeline snapshots */}
                  {events.length > 0 && (
                    <View style={styles.timelineContainer}>
                      <ThemedText type="smallBold" style={styles.timelineHeader}>
                        Timeline Events
                      </ThemedText>
                      {events.map((ev: any, index: number) => (
                        <View key={`ev-${index}`} style={styles.timelineRow}>
                          <ThemedText style={styles.timelineDot}>•</ThemedText>
                          <ThemedText style={styles.timelineDate}>{ev.date}: </ThemedText>
                          <ThemedText style={styles.timelineLabel}>{ev.label}</ThemedText>
                        </View>
                      ))}
                      {warnings.map((warn: string, index: number) => (
                        <View key={`warn-${index}`} style={styles.warningRow}>
                          <SymbolView name="exclamationmark.triangle.fill" size={12} tintColor="#EF4444" />
                          <ThemedText style={styles.warningText}>{warn}</ThemedText>
                        </View>
                      ))}
                    </View>
                  )}

                  {/* Quick Action Buttons */}
                  <View style={styles.actionsRow}>
                    <TouchableOpacity
                      style={[styles.actionBtn, styles.waterBtn]}
                      onPress={() => waterOne(plant.id)}
                    >
                      <SymbolView name="drop.fill" size={14} tintColor="#fff" />
                      <ThemedText style={styles.btnTextWhite}>Water</ThemedText>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={[styles.actionBtn, styles.dupBtn]}
                      onPress={() => handleDuplicate(plant.id)}
                    >
                      <SymbolView name="doc.on.doc.fill" size={14} tintColor="#fff" />
                      <ThemedText style={styles.btnTextWhite}>Duplicate</ThemedText>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={[styles.actionBtn, styles.editBtn]}
                      onPress={() => openEditModal(plant)}
                    >
                      <SymbolView name="pencil" size={14} tintColor="#fff" />
                      <ThemedText style={styles.btnTextWhite}>Edit</ThemedText>
                    </TouchableOpacity>
                  </View>
                </ThemedView>
              );
            })}
          </ScrollView>
        )}
      </SafeAreaView>

      {/* Add Modal */}
      <Modal
        visible={addModalVisible}
        animationType="slide"
        onRequestClose={() => setAddModalVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle" style={styles.modalTitle}>Add New Plant</ThemedText>
            <TouchableOpacity onPress={() => setAddModalVisible(false)} style={styles.closeHeaderBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <ThemedText style={styles.closeHeaderText}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Plant Name *</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Cherry Tomato"
              placeholderTextColor="#888"
              value={name}
              onChangeText={setName}
            />

            <ThemedText style={styles.fieldLabel}>Scientific Name Override</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Solanum lycopersicum"
              placeholderTextColor="#888"
              value={speciesName}
              onChangeText={setSpeciesName}
            />

            <ThemedText style={styles.fieldLabel}>Plant Type</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.typeSelector}>
              {PLANT_TYPES.map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeOption,
                    plantType === type && styles.typeOptionSelected,
                  ]}
                  onPress={() => setPlantType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      plantType === type && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {type}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <ThemedText style={styles.fieldLabel}>Growing Location</ThemedText>
            {locations.length === 0 ? (
              <ThemedText themeColor="textSecondary" style={styles.warnText}>
                No locations available. Please create one on the settings tab first.
              </ThemedText>
            ) : (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.typeSelector}>
                {locations.map((loc) => (
                  <TouchableOpacity
                    key={loc.id}
                    style={[
                      styles.typeOption,
                      locationId === loc.id && styles.typeOptionSelected,
                    ]}
                    onPress={() => setLocationId(loc.id)}
                  >
                    <ThemedText
                      style={[
                        styles.typeOptionText,
                        locationId === loc.id && { color: '#fff', fontWeight: 'bold' },
                      ]}
                    >
                      {loc.name}
                    </ThemedText>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            )}

            <View style={styles.switchRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Uses Soil Sensor</ThemedText>
                <ThemedText type="small" style={styles.modalHelperText}>
                  Enable dynamic sensor reading overrides.
                </ThemedText>
              </View>
              <Switch value={useSensor} onValueChange={setUseSensor} trackColor={{ true: '#10B981' }} />
            </View>

            <ThemedText style={styles.fieldLabel}>Watering Interval (Days)</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. 5"
              placeholderTextColor="#888"
              keyboardType="number-pad"
              value={wateringInterval}
              onChangeText={setWateringInterval}
            />

            <View style={styles.speciesCardHeader}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Perenual API Species ID</ThemedText>
                <ThemedText type="small" style={styles.modalHelperText}>
                  Link with global Perenual database for enrichment.
                </ThemedText>
              </View>
              <TouchableOpacity
                style={styles.searchLink}
                onPress={() => {
                  setAddModalVisible(false);
                  router.push('/species-search');
                }}
              >
                <SymbolView name="magnifyingglass" size={14} tintColor="#10B981" />
                <ThemedText style={styles.searchLinkText}>Search ID</ThemedText>
              </TouchableOpacity>
            </View>
            <TextInput
              style={styles.input}
              placeholder="e.g. 1 (Set 0 to skip)"
              placeholderTextColor="#888"
              keyboardType="number-pad"
              value={speciesId}
              onChangeText={setSpeciesId}
            />

            <View style={styles.modalButtonGroup}>
              <TouchableOpacity
                style={[styles.submitBtn, styles.cancelBtn]}
                onPress={() => setAddModalVisible(false)}
                disabled={formLoading}
              >
                <ThemedText style={styles.cancelBtnText}>Cancel</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.submitBtn, styles.primarySubmitBtn]}
                onPress={handleCreatePlant}
                disabled={formLoading}
              >
                {formLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <ThemedText style={styles.submitBtnText}>Create Plant</ThemedText>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Modal */}
      <Modal
        visible={editModalVisible}
        animationType="slide"
        onRequestClose={() => setEditModalVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle" style={styles.modalTitle}>Edit Plant Details</ThemedText>
            <TouchableOpacity onPress={() => setEditModalVisible(false)} style={styles.closeHeaderBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <ThemedText style={styles.closeHeaderText}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Plant Name *</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Cherry Tomato"
              placeholderTextColor="#888"
              value={editName}
              onChangeText={setEditName}
            />

            <ThemedText style={styles.fieldLabel}>Scientific Name Override</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Solanum lycopersicum"
              placeholderTextColor="#888"
              value={editSpeciesName}
              onChangeText={setEditSpeciesName}
            />

            <ThemedText style={styles.fieldLabel}>Plant Type</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.typeSelector}>
              {PLANT_TYPES.map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeOption,
                    editPlantType === type && styles.typeOptionSelected,
                  ]}
                  onPress={() => setEditPlantType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      editPlantType === type && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {type}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <ThemedText style={styles.fieldLabel}>Growing Location</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.typeSelector}>
              {locations.map((loc) => (
                <TouchableOpacity
                  key={loc.id}
                  style={[
                    styles.typeOption,
                    editLocationId === loc.id && styles.typeOptionSelected,
                  ]}
                  onPress={() => setEditLocationId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      editLocationId === loc.id && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {loc.name}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.switchRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Uses Soil Sensor</ThemedText>
                <ThemedText type="small" style={styles.modalHelperText}>
                  Enable dynamic sensor reading overrides.
                </ThemedText>
              </View>
              <Switch value={editUseSensor} onValueChange={setEditUseSensor} trackColor={{ true: '#10B981' }} />
            </View>

            <ThemedText style={styles.fieldLabel}>Watering Interval (Days)</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. 5"
              placeholderTextColor="#888"
              keyboardType="number-pad"
              value={editWateringInterval}
              onChangeText={setEditWateringInterval}
            />

            <View style={styles.modalButtonGroup}>
              <TouchableOpacity
                style={[styles.submitBtn, styles.cancelBtn]}
                onPress={() => setEditModalVisible(false)}
                disabled={formLoading}
              >
                <ThemedText style={styles.cancelBtnText}>Cancel</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.submitBtn, styles.primarySubmitBtn]}
                onPress={handleUpdatePlant}
                disabled={formLoading}
              >
                {formLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <ThemedText style={styles.submitBtnText}>Save Changes</ThemedText>
                )}
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[styles.submitBtn, styles.deleteBtn]}
              onPress={() => selectedPlant && handleDeletePlant(selectedPlant.id, selectedPlant.name)}
              disabled={formLoading || !selectedPlant}
            >
              {formLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <ThemedText style={styles.submitBtnText}>Delete Plant</ThemedText>
              )}
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
    padding: Spacing.four,
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
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: Spacing.two,
    marginHorizontal: Spacing.three,
    marginBottom: Spacing.three,
    paddingHorizontal: Spacing.three,
    height: 44,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '90%',
  },
  searchIcon: {
    marginRight: Spacing.two,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
    color: '#000',
  },
  listContainer: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  emptyContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.four,
  },
  emptyText: {
    fontSize: 14,
    marginTop: Spacing.two,
    textAlign: 'center',
  },
  plantCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.three,
  },
  plantHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: Spacing.two,
    gap: Spacing.two,
  },
  plantName: {
    fontSize: 18,
  },
  plantSciName: {
    fontSize: 13,
    fontStyle: 'italic',
    marginTop: 2,
  },
  badgeContainer: {
    flexDirection: 'row',
    gap: 6,
  },
  typeBadge: {
    backgroundColor: 'rgba(16, 185, 129, 0.12)',
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  locBadge: {
    backgroundColor: 'rgba(59, 130, 246, 0.12)',
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#374151',
  },
  metadataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: 'rgba(0,0,0,0.02)',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginBottom: Spacing.two,
  },
  metaItem: {
    alignItems: 'center',
  },
  metaLabel: {
    fontSize: 10,
    marginBottom: 2,
  },
  taxonomyRow: {
    marginBottom: Spacing.two,
  },
  taxonomyText: {
    fontSize: 12,
  },
  timelineContainer: {
    backgroundColor: 'rgba(0,0,0,0.03)',
    padding: Spacing.three,
    borderRadius: Spacing.two,
    marginBottom: Spacing.three,
  },
  timelineHeader: {
    fontSize: 14,
    marginBottom: Spacing.one,
  },
  timelineRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  timelineDot: {
    color: '#10B981',
    marginRight: 6,
    fontSize: 16,
  },
  timelineDate: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  timelineLabel: {
    fontSize: 12,
    flex: 1,
  },
  warningRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    gap: Spacing.one,
  },
  warningText: {
    fontSize: 11,
    color: '#EF4444',
    flex: 1,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    gap: Spacing.two,
  },
  actionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    gap: Spacing.one,
  },
  waterBtn: {
    backgroundColor: '#06B6D4',
  },
  dupBtn: {
    backgroundColor: '#3B82F6',
  },
  editBtn: {
    backgroundColor: '#8B5CF6',
  },
  btnTextWhite: {
    color: '#fff',
    fontSize: 13,
    fontWeight: 'bold',
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
  modalTitle: {
    color: '#111827',
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: Spacing.three,
    marginBottom: Spacing.one,
    color: '#111827',
  },
  modalHelperText: {
    color: '#6B7280',
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
  typeSelector: {
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
  switchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: Spacing.three,
    marginBottom: Spacing.two,
  },
  speciesCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginTop: Spacing.two,
  },
  searchLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    padding: 4,
  },
  searchLinkText: {
    fontSize: 12,
    color: '#10B981',
    fontWeight: 'bold',
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
    backgroundColor: '#EF4444',
    marginTop: Spacing.two,
  },
  warnText: {
    fontSize: 12,
    color: '#D97706',
    marginVertical: Spacing.one,
  },
  modalButtonGroup: {
    flexDirection: 'row',
    gap: Spacing.two,
    marginTop: Spacing.four,
  },
  primarySubmitBtn: {
    flex: 1,
    marginTop: 0,
  },
  cancelBtn: {
    backgroundColor: '#F3F4F6',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    flex: 1,
    marginTop: 0,
  },
  cancelBtnText: {
    color: '#374151',
    fontSize: 16,
    fontWeight: '600',
  },
  closeHeaderBtn: {
    padding: Spacing.one,
  },
  closeHeaderText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#6B7280',
  },
});
