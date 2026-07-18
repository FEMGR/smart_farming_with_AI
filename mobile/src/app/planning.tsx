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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useRouter } from 'expo-router';
import { useData } from '@/context/DataContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function PlanningScreen() {
  const router = useRouter();
  const {
    locations,
    sections,
    savedPlans,
    addSection,
    editSection,
    removeSection,
    removePolyculturePlan,
    getPolyculturePreview,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const [activeTab, setActiveTab] = useState<'plans' | 'sections' | 'preview'>('plans');

  // Form Section States
  const [sectionModalVisible, setSectionModalVisible] = useState(false);
  const [editSectionModalVisible, setEditSectionModalVisible] = useState(false);
  const [selectedSection, setSelectedSection] = useState<any>(null);

  // New Section Fields
  const [secName, setSecName] = useState('');
  const [secType, setSecType] = useState('production');
  const [secWidth, setSecWidth] = useState('2.0');
  const [secLength, setSecLength] = useState('3.0');
  const [secLocationId, setSecLocationId] = useState<number | null>(null);

  // Edit Section Fields
  const [editSecName, setEditSecName] = useState('');
  const [editSecType, setEditSecType] = useState('production');
  const [editSecWidth, setEditSecWidth] = useState('2.0');
  const [editSecLength, setEditSecLength] = useState('3.0');
  const [editSecLocationId, setEditSecLocationId] = useState<number | null>(null);

  // Polyculture Preview Fields
  const [previewLocId, setPreviewLocId] = useState<number | null>(null);
  const [previewSecIds, setPreviewSecIds] = useState<number[]>([]);
  const [cropsText, setCropsText] = useState('cabbage, tomato, carrot, cucumber, lettuce, potato, asparagus');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [harvestInterval, setHarvestInterval] = useState('14');
  const [batchesWanted, setBatchesWanted] = useState('0');
  const [variationsPerGroup, setVariationsPerGroup] = useState('2');

  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (locations.length > 0) {
      if (secLocationId === null) setSecLocationId(locations[0].id);
      if (previewLocId === null) setPreviewLocId(locations[0].id);
    }
  }, [locations]);

  // Handle Location changes for section lists in Preview form
  useEffect(() => {
    if (previewLocId !== null) {
      const locSections = sections.filter((s) => s.location_id === previewLocId);
      setPreviewSecIds(locSections.map((s) => s.id));
    }
  }, [previewLocId, sections]);

  const handleCreateSection = async () => {
    if (!secName.trim()) {
      Alert.alert('Error', 'Section name is required');
      return;
    }
    setActionLoading(true);
    try {
      const w = parseFloat(secWidth) || 1.0;
      const l = parseFloat(secLength) || 1.0;
      await addSection({
        location_id: secLocationId,
        name: secName.trim(),
        section_type: secType,
        width_m: w,
        length_m: l,
        area_m2: w * l,
      });
      setSectionModalVisible(false);
      setSecName('');
      Alert.alert('Success', 'Section created successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to create section');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUpdateSection = async () => {
    if (!editSecName.trim()) {
      Alert.alert('Error', 'Section name is required');
      return;
    }
    setActionLoading(true);
    try {
      const w = parseFloat(editSecWidth) || 1.0;
      const l = parseFloat(editSecLength) || 1.0;
      await editSection(selectedSection.id, {
        location_id: editSecLocationId,
        name: editSecName.trim(),
        section_type: editSecType,
        width_m: w,
        length_m: l,
        area_m2: w * l,
      });
      setEditSectionModalVisible(false);
      Alert.alert('Success', 'Section updated successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to update section');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteSection = (secId: number, name: string) => {
    Alert.alert(
      'Confirm Delete',
      `Delete farm section "${name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await removeSection(secId);
              setEditSectionModalVisible(false);
            } catch (e: any) {
              Alert.alert('Error', e.message || 'Failed to delete section');
            }
          },
        },
      ]
    );
  };

  const openEditSection = (sec: any) => {
    setSelectedSection(sec);
    setEditSecName(sec.name || '');
    setEditSecType(sec.section_type || 'production');
    setEditSecWidth(String(sec.width_m || 2.0));
    setEditSecLength(String(sec.length_m || 3.0));
    setEditSecLocationId(sec.location_id || (locations[0]?.id || null));
    setEditSectionModalVisible(true);
  };

  const handleGeneratePreview = async () => {
    if (previewSecIds.length === 0) {
      Alert.alert('Error', 'Please select at least one farm section');
      return;
    }

    const intendedCrops = cropsText
      .split(',')
      .map((c) => c.trim())
      .filter((c) => c.length > 0);

    if (intendedCrops.length === 0) {
      Alert.alert('Error', 'Please enter at least one intended crop');
      return;
    }

    setActionLoading(true);
    try {
      const payload: any = {
        location_id: previewLocId,
        section_ids: previewSecIds,
        intended_crops: intendedCrops,
        start_date: startDate,
        harvest_interval_days: parseInt(harvestInterval) || 14,
      };

      const batches = parseInt(batchesWanted) || 0;
      if (batches > 0) payload.desired_harvest_batches = batches;

      const variations = parseInt(variationsPerGroup) || 0;
      if (variations > 0) payload.plant_variations_per_group = variations;

      const previewResult = await getPolyculturePreview(payload);
      
      // Save payload and result temporarily in AsyncStorage to pass to preview screen
      await AsyncStorage.setItem('pending_preview_payload', JSON.stringify(payload));
      await AsyncStorage.setItem('pending_preview_result', JSON.stringify(previewResult));
      
      router.push('/plan-preview');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to generate preview');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeletePlan = (planId: number, planName: string) => {
    Alert.alert(
      'Confirm Delete',
      `Delete polyculture plan "${planName}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await removePolyculturePlan(planId);
            } catch (e: any) {
              Alert.alert('Error', e.message || 'Failed to delete plan');
            }
          },
        },
      ]
    );
  };

  const toggleSectionSelection = (id: number) => {
    if (previewSecIds.includes(id)) {
      setPreviewSecIds(previewSecIds.filter((x) => x !== id));
    } else {
      setPreviewSecIds([...previewSecIds, id]);
    }
  };

  const getCropsComboText = (plan: any) => {
    const crops: string[] = [];
    (plan.groups || []).forEach((g: any) => {
      crops.push(...(g.main_crops || []));
    });
    const unique = Array.from(new Set(crops));
    return unique.join(', ') || 'No plants';
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <ThemedText type="subtitle" style={styles.title}>
              Planning
            </ThemedText>
            <ThemedText themeColor="textSecondary">
              Polyculture production planning
            </ThemedText>
          </View>
          {activeTab === 'sections' && (
            <TouchableOpacity
              style={styles.addButton}
              onPress={() => setSectionModalVisible(true)}
            >
              <SymbolView name="plus" size={16} tintColor="#fff" />
              <ThemedText style={styles.addButtonText}>Add Section</ThemedText>
            </TouchableOpacity>
          )}
        </View>

        {/* Tab Segment Selector */}
        <View style={styles.tabBar}>
          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'plans' && styles.tabItemActive]}
            onPress={() => setActiveTab('plans')}
          >
            <ThemedText style={[styles.tabLabel, activeTab === 'plans' && styles.tabLabelActive]}>
              Saved Plans
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'sections' && styles.tabItemActive]}
            onPress={() => setActiveTab('sections')}
          >
            <ThemedText style={[styles.tabLabel, activeTab === 'sections' && styles.tabLabelActive]}>
              Sections
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabItem, activeTab === 'preview' && styles.tabItemActive]}
            onPress={() => setActiveTab('preview')}
          >
            <ThemedText style={[styles.tabLabel, activeTab === 'preview' && styles.tabLabelActive]}>
              Preview Generator
            </ThemedText>
          </TouchableOpacity>
        </View>

        {/* Tab Contents */}
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : activeTab === 'plans' ? (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {savedPlans.length === 0 ? (
              <View style={styles.empty}>
                <SymbolView name="calendar.badge.plus" size={48} tintColor="#ccc" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  No saved polyculture plans yet. Use the preview generator to create one!
                </ThemedText>
              </View>
            ) : (
              savedPlans.map((plan) => (
                <ThemedView key={plan.id} type="backgroundElement" style={styles.card}>
                  <View style={styles.cardHeader}>
                    <View style={{ flex: 1 }}>
                      <ThemedText type="smallBold" style={styles.planName}>
                        {plan.name || 'Polyculture Plan'}
                      </ThemedText>
                      <ThemedText themeColor="textSecondary" style={styles.planCombo}>
                        {getCropsComboText(plan)}
                      </ThemedText>
                    </View>
                    <TouchableOpacity
                      onPress={() => handleDeletePlan(plan.id, plan.name)}
                      style={styles.deletePlanBtn}
                    >
                      <SymbolView name="trash.fill" size={16} tintColor="#EF4444" />
                    </TouchableOpacity>
                  </View>

                  <View style={styles.planDetailsGrid}>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Status
                      </ThemedText>
                      <ThemedText type="smallBold">{plan.status}</ThemedText>
                    </View>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Harvest Int.
                      </ThemedText>
                      <ThemedText type="smallBold">{plan.desired_harvest_interval_days} days</ThemedText>
                    </View>
                    <View style={styles.detailBox}>
                      <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                        Groups
                      </ThemedText>
                      <ThemedText type="smallBold">{plan.group_count}</ThemedText>
                    </View>
                  </View>

                  {/* Render groups */}
                  {(plan.groups || []).map((g: any, index: number) => (
                    <View key={`g-${index}`} style={styles.groupSubCard}>
                      <ThemedText type="smallBold" style={styles.groupSubTitle}>
                        Group {g.group_id} - {g.section_name || 'Not assigned'}
                      </ThemedText>
                      <ThemedText type="small" themeColor="textSecondary">
                        Allocated: {g.allocated_area_m2} m²
                      </ThemedText>
                      <ThemedText type="small" style={styles.cropsLabel}>
                        Crops: {g.main_crops?.join(', ')}
                      </ThemedText>

                      {/* Batches/Timelines */}
                      {g.batches && g.batches.length > 0 && (
                        <View style={styles.batchesContainer}>
                          {g.batches.map((b: any, bIdx: number) => (
                            <View key={`b-${bIdx}`} style={styles.batchRow}>
                              <ThemedText style={styles.batchIdx}>Batch {b.batch_number}: </ThemedText>
                              <ThemedText style={styles.batchDates}>
                                {b.seed_start_date} → {b.expected_harvest_date}
                              </ThemedText>
                            </View>
                          ))}
                        </View>
                      )}
                    </View>
                  ))}
                </ThemedView>
              ))
            )}
          </ScrollView>
        ) : activeTab === 'sections' ? (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {sections.length === 0 ? (
              <View style={styles.empty}>
                <SymbolView name="square.grid.2x2.fill" size={48} tintColor="#ccc" />
                <ThemedText themeColor="textSecondary" style={styles.emptyText}>
                  No farm sections created. Click '+' at the top right to create one!
                </ThemedText>
              </View>
            ) : (
              sections.map((sec) => {
                const loc = locations.find((l) => l.id === sec.location_id);
                return (
                  <ThemedView key={sec.id} type="backgroundElement" style={styles.card}>
                    <View style={styles.cardHeader}>
                      <View style={{ flex: 1 }}>
                        <ThemedText type="smallBold" style={styles.sectionTitleText}>
                          {sec.name}
                        </ThemedText>
                        <ThemedText themeColor="textSecondary" style={styles.sectionLocText}>
                          Location: {loc?.name || `ID ${sec.location_id}`}
                        </ThemedText>
                      </View>
                      <TouchableOpacity onPress={() => openEditSection(sec)} style={styles.editSecBtn}>
                        <SymbolView name="pencil" size={16} tintColor="#10B981" />
                      </TouchableOpacity>
                    </View>

                    <View style={styles.secDetailsGrid}>
                      <View style={styles.detailBox}>
                        <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                          Type
                        </ThemedText>
                        <ThemedText type="smallBold">{sec.section_type}</ThemedText>
                      </View>
                      <View style={styles.detailBox}>
                        <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                          Dimensions
                        </ThemedText>
                        <ThemedText type="smallBold">
                          {sec.width_m} m x {sec.length_m} m
                        </ThemedText>
                      </View>
                      <View style={styles.detailBox}>
                        <ThemedText themeColor="textSecondary" style={styles.detailLabel}>
                          Area
                        </ThemedText>
                        <ThemedText type="smallBold">{sec.area_m2?.toFixed(1)} m²</ThemedText>
                      </View>
                    </View>
                  </ThemedView>
                );
              })
            )}
          </ScrollView>
        ) : (
          /* PREVIEW GENERATOR FORM */
          <ScrollView contentContainerStyle={styles.scrollForm}>
            <ThemedText style={styles.fieldLabel}>Select Location</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {locations.map((loc) => (
                <TouchableOpacity
                  key={loc.id}
                  style={[
                    styles.typeOption,
                    previewLocId === loc.id && styles.typeOptionSelected,
                  ]}
                  onPress={() => setPreviewLocId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      previewLocId === loc.id && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {loc.name}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <ThemedText style={styles.fieldLabel}>Select Sections to Include</ThemedText>
            {sections.filter((s) => s.location_id === previewLocId).length === 0 ? (
              <ThemedText themeColor="textSecondary" style={styles.warnText}>
                No sections available in this location. Please create a section first.
              </ThemedText>
            ) : (
              <View style={styles.multiselectGrid}>
                {sections
                  .filter((s) => s.location_id === previewLocId)
                  .map((s) => {
                    const isSelected = previewSecIds.includes(s.id);
                    return (
                      <TouchableOpacity
                        key={s.id}
                        style={[
                          styles.secMultiBtn,
                          isSelected && styles.secMultiBtnSelected,
                        ]}
                        onPress={() => toggleSectionSelection(s.id)}
                      >
                        <SymbolView
                          name={isSelected ? 'checkmark.square.fill' : 'square'}
                          size={14}
                          tintColor={isSelected ? '#fff' : '#888'}
                        />
                        <ThemedText
                          style={[
                            styles.secMultiBtnText,
                            isSelected && { color: '#fff', fontWeight: 'bold' },
                          ]}
                        >
                          {s.name} ({s.area_m2}m²)
                        </ThemedText>
                      </TouchableOpacity>
                    );
                  })}
              </View>
            )}

            <ThemedText style={styles.fieldLabel}>Intended Crop Mix (Comma separated)</ThemedText>
            <TextInput
              style={[styles.input, styles.multilineInput]}
              multiline
              numberOfLines={3}
              value={cropsText}
              onChangeText={setCropsText}
            />

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Start Date</ThemedText>
                <TextInput
                  style={styles.input}
                  value={startDate}
                  onChangeText={setStartDate}
                  placeholder="YYYY-MM-DD"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Harvest Interval (Days)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={harvestInterval}
                  onChangeText={setHarvestInterval}
                  keyboardType="number-pad"
                />
              </View>
            </View>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Harvest Batches</ThemedText>
                <TextInput
                  style={styles.input}
                  value={batchesWanted}
                  onChangeText={setBatchesWanted}
                  keyboardType="number-pad"
                  placeholder="0 for auto"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Variations per Group</ThemedText>
                <TextInput
                  style={styles.input}
                  value={variationsPerGroup}
                  onChangeText={setVariationsPerGroup}
                  keyboardType="number-pad"
                  placeholder="2"
                />
              </View>
            </View>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handleGeneratePreview}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <>
                  <SymbolView name="wand.and.stars" size={16} tintColor="#fff" style={{ marginRight: 6 }} />
                  <ThemedText style={styles.submitBtnText}>Generate Polyculture Preview</ThemedText>
                </>
              )}
            </TouchableOpacity>
          </ScrollView>
        )}
      </SafeAreaView>

      {/* Add Section Modal */}
      <Modal
        visible={sectionModalVisible}
        animationType="slide"
        onRequestClose={() => setSectionModalVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle">Create Farm Section</ThemedText>
            <TouchableOpacity onPress={() => setSectionModalVisible(false)}>
              <SymbolView name="xmark" size={24} tintColor="#10B981" />
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Section Name *</ThemedText>
            <TextInput
              style={styles.input}
              placeholder="e.g. Bed A, Row 1, Greenhouse Shelf B"
              placeholderTextColor="#888"
              value={secName}
              onChangeText={setSecName}
            />

            <ThemedText style={styles.fieldLabel}>Location</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {locations.map((loc) => (
                <TouchableOpacity
                  key={loc.id}
                  style={[
                    styles.typeOption,
                    secLocationId === loc.id && styles.typeOptionSelected,
                  ]}
                  onPress={() => setSecLocationId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      secLocationId === loc.id && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {loc.name}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <ThemedText style={styles.fieldLabel}>Section Type</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {['production', 'nursery', 'reserve'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeOption,
                    secType === type && styles.typeOptionSelected,
                  ]}
                  onPress={() => setSecType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      secType === type && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {type}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Width (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={secWidth}
                  onChangeText={setSecWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={secLength}
                  onChangeText={setSecLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handleCreateSection}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <ThemedText style={styles.submitBtnText}>Create Section</ThemedText>
              )}
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Section Modal */}
      <Modal
        visible={editSectionModalVisible}
        animationType="slide"
        onRequestClose={() => setEditSectionModalVisible(false)}
      >
        <SafeAreaView style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <ThemedText type="subtitle">Edit Farm Section</ThemedText>
            <TouchableOpacity onPress={() => setEditSectionModalVisible(false)}>
              <SymbolView name="xmark" size={24} tintColor="#10B981" />
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Section Name *</ThemedText>
            <TextInput
              style={styles.input}
              value={editSecName}
              onChangeText={setEditSecName}
            />

            <ThemedText style={styles.fieldLabel}>Location</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {locations.map((loc) => (
                <TouchableOpacity
                  key={loc.id}
                  style={[
                    styles.typeOption,
                    editSecLocationId === loc.id && styles.typeOptionSelected,
                  ]}
                  onPress={() => setEditSecLocationId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      editSecLocationId === loc.id && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {loc.name}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <ThemedText style={styles.fieldLabel}>Section Type</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {['production', 'nursery', 'reserve'].map((type) => (
                <TouchableOpacity
                  key={type}
                  style={[
                    styles.typeOption,
                    editSecType === type && styles.typeOptionSelected,
                  ]}
                  onPress={() => setEditSecType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      editSecType === type && { color: '#fff', fontWeight: 'bold' },
                    ]}
                  >
                    {type}
                  </ThemedText>
                </TouchableOpacity>
              ))}
            </ScrollView>

            <View style={styles.formRow}>
              <View style={{ flex: 1 }}>
                <ThemedText style={styles.fieldLabel}>Width (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={editSecWidth}
                  onChangeText={setEditSecWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={styles.input}
                  value={editSecLength}
                  onChangeText={setEditSecLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <TouchableOpacity
              style={styles.submitBtn}
              onPress={handleUpdateSection}
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
              onPress={() => handleDeleteSection(selectedSection.id, selectedSection.name)}
              disabled={actionLoading}
            >
              <ThemedText style={styles.submitBtnText}>Delete Section</ThemedText>
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
    marginBottom: Spacing.two,
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
  tabBar: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(0,0,0,0.08)',
    marginHorizontal: Spacing.three,
    marginBottom: Spacing.three,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '90%',
  },
  tabItem: {
    flex: 1,
    paddingVertical: Spacing.two,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabItemActive: {
    borderBottomColor: '#10B981',
  },
  tabLabel: {
    fontSize: 14,
    color: '#888',
  },
  tabLabelActive: {
    color: '#10B981',
    fontWeight: 'bold',
  },
  scrollContent: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  scrollForm: {
    paddingHorizontal: Spacing.four,
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
  planName: {
    fontSize: 16,
  },
  planCombo: {
    fontSize: 12,
    marginTop: 2,
  },
  deletePlanBtn: {
    padding: Spacing.one,
  },
  planDetailsGrid: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.02)',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginBottom: Spacing.three,
  },
  detailBox: {
    flex: 1,
    alignItems: 'center',
  },
  detailLabel: {
    fontSize: 10,
    marginBottom: 2,
  },
  groupSubCard: {
    backgroundColor: 'rgba(0,0,0,0.03)',
    borderRadius: Spacing.two,
    padding: Spacing.three,
    marginBottom: Spacing.two,
  },
  groupSubTitle: {
    fontSize: 14,
    marginBottom: 2,
  },
  cropsLabel: {
    marginTop: Spacing.one,
    fontWeight: '500',
  },
  batchesContainer: {
    marginTop: Spacing.two,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
    paddingTop: Spacing.one,
  },
  batchRow: {
    flexDirection: 'row',
    marginTop: 2,
  },
  batchIdx: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  batchDates: {
    fontSize: 11,
  },
  sectionTitleText: {
    fontSize: 16,
  },
  sectionLocText: {
    fontSize: 12,
    marginTop: 2,
  },
  editSecBtn: {
    padding: Spacing.one,
  },
  secDetailsGrid: {
    flexDirection: 'row',
    backgroundColor: 'rgba(0,0,0,0.02)',
    padding: Spacing.two,
    borderRadius: Spacing.two,
    marginTop: Spacing.two,
  },
  fieldLabel: {
    fontSize: 14,
    fontWeight: 'bold',
    marginTop: Spacing.three,
    marginBottom: Spacing.one,
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
  multilineInput: {
    height: 80,
    paddingTop: Spacing.two,
    textAlignVertical: 'top',
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
    marginTop: Spacing.four,
    flexDirection: 'row',
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 16,
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
  deleteBtn: {
    backgroundColor: '#EF4444',
    marginTop: Spacing.two,
  },
  warnText: {
    fontSize: 12,
    color: '#D97706',
    marginVertical: Spacing.one,
  },
  multiselectGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.two,
    marginBottom: Spacing.two,
    marginTop: Spacing.one,
  },
  secMultiBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ccc',
    gap: Spacing.one,
  },
  secMultiBtnSelected: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
  },
  secMultiBtnText: {
    fontSize: 13,
    color: '#333',
  },
});
