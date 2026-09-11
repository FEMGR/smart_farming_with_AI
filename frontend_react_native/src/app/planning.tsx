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
import { useTheme } from '@/hooks/use-theme';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function PlanningScreen() {
  const colors = useTheme();
  const router = useRouter();
  const {
    locations,
    sections,
    savedPlans,
    addSection,
    editSection,
    removeSection,
    editLocation,
    removeLocation,
    removePolyculturePlan,
    getPolyculturePreview,
    loading,
    refreshAll,
    refreshing,
  } = useData();

  const [expandedSection, setExpandedSection] = useState<string | null>('plans');

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

  // Form Section States
  const [sectionModalVisible, setSectionModalVisible] = useState(false);
  const [editSectionModalVisible, setEditSectionModalVisible] = useState(false);
  const [selectedSection, setSelectedSection] = useState<any>(null);

  // Form Location States
  const [editLocModalVisible, setEditLocModalVisible] = useState(false);
  const [selectedLoc, setSelectedLoc] = useState<any>(null);
  const [editLocName, setEditLocName] = useState('');
  const [editLocDesc, setEditLocDesc] = useState('');
  const [editLocEnv, setEditLocEnv] = useState('outdoor');
  const [editLocWidth, setEditLocWidth] = useState('5.0');
  const [editLocLength, setEditLocLength] = useState('5.0');
  const [editLocLat, setEditLocLat] = useState('');
  const [editLocLng, setEditLocLng] = useState('');

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

  const openEditLocation = (loc: any) => {
    if (!loc) return;
    setSelectedLoc(loc);
    setEditLocName(loc.name || '');
    setEditLocDesc(loc.description || '');
    setEditLocEnv(loc.environment_type || 'outdoor');
    setEditLocWidth(String(loc.width_m || 5.0));
    setEditLocLength(String(loc.length_m || 5.0));
    setEditLocLat(loc.latitude ? String(loc.latitude) : '');
    setEditLocLng(loc.longitude ? String(loc.longitude) : '');
    setEditLocModalVisible(true);
  };

  const handleUpdateLocation = async () => {
    if (!selectedLoc || !editLocName.trim()) {
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
      setEditLocModalVisible(false);
      Alert.alert('Success', 'Location updated successfully');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to update location');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteLocation = (locId: number, name: string) => {
    Alert.alert(
      'Delete Location',
      `Are you sure you want to delete "${name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            setActionLoading(true);
            try {
              await removeLocation(locId);
              setEditLocModalVisible(false);
            } catch (e: any) {
              Alert.alert('Error', e.message || 'Failed to delete location');
            } finally {
              setActionLoading(false);
            }
          },
        },
      ]
    );
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
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setSectionModalVisible(true)}
          >
            <SymbolView name="plus" size={16} tintColor="#fff" />
            <ThemedText style={styles.addButtonText}>Add Section</ThemedText>
          </TouchableOpacity>
        </View>

        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : (
          <ScrollView
            contentContainerStyle={styles.scrollContent}
            refreshControl={
              <RefreshControl refreshing={refreshing} onRefresh={refreshAll} />
            }
          >
            {/* Item 1: Saved Polyculture Plans */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'plans',
                'Saved Polyculture Plans',
                `Saved: ${savedPlans.length} plans`,
                savedPlans.length,
                savedPlans.length || 1,
                1.0
              )}

              {expandedSection === 'plans' && (
                <View style={{ paddingTop: Spacing.two }}>
                  {savedPlans.length === 0 ? (
                    <View style={styles.empty}>
                      <SymbolView name="calendar.badge.plus" size={48} tintColor={colors.placeholder} />
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
                            <SymbolView name="trash.fill" size={16} tintColor={colors.badgeErrorText} />
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
                </View>
              )}
            </View>

            {/* Item 2: Farm Sections */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'sections',
                'Farm Sections & Capacity',
                `Sections: ${sections.length} active`,
                sections.length,
                sections.length || 1,
                1.0
              )}

              {expandedSection === 'sections' && (
                <View style={{ paddingTop: Spacing.two }}>
                  {sections.length === 0 ? (
                    <View style={styles.empty}>
                      <SymbolView name="square.grid.2x2.fill" size={48} tintColor={colors.placeholder} />
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
                              <TouchableOpacity onPress={() => openEditSection(sec)} activeOpacity={0.7}>
                                <ThemedText type="smallBold" style={styles.sectionTitleText}>
                                  {sec.name}
                                </ThemedText>
                              </TouchableOpacity>
                              <TouchableOpacity
                                onPress={() => loc && openEditLocation(loc)}
                                activeOpacity={0.7}
                                style={styles.locationLinkBtn}
                              >
                                <ThemedText themeColor="textSecondary" style={styles.sectionLocText}>
                                  Location: <ThemedText style={styles.locNameHighlight}>{loc?.name || `ID ${sec.location_id}`}</ThemedText> ✎
                                </ThemedText>
                              </TouchableOpacity>
                            </View>
                            <TouchableOpacity onPress={() => openEditSection(sec)} style={styles.editSecBtn}>
                              <SymbolView name="pencil" size={16} tintColor={colors.emerald} />
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
                              <ThemedText type="smallBold">{Number(sec.area_m2 || 0).toFixed(1)} m²</ThemedText>
                            </View>
                          </View>
                        </ThemedView>
                      );
                    })
                  )}
                </View>
              )}
            </View>

            {/* Item 3: Preview Generator */}
            <View style={{ marginBottom: Spacing.three }}>
              {renderAccordionHeader(
                'preview',
                'Polyculture Plan Generator & Preview',
                'Interactive Generator',
                1,
                1,
                1.0
              )}

              {expandedSection === 'preview' && (
                <View style={{ paddingTop: Spacing.two }}>
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
                                {
                                  backgroundColor: isSelected ? colors.primary : colors.backgroundElement,
                                  borderColor: isSelected ? colors.primary : colors.border,
                                },
                              ]}
                              onPress={() => toggleSectionSelection(s.id)}
                            >
                              <SymbolView
                                name={isSelected ? 'checkmark.square.fill' : 'square'}
                                size={14}
                                tintColor={isSelected ? colors.textInverse : colors.primary}
                              />
                              <ThemedText
                                style={[
                                  styles.secMultiBtnText,
                                  { color: isSelected ? colors.textInverse : colors.text },
                                  isSelected && { fontWeight: 'bold' },
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
                    style={[
                      styles.input,
                      styles.multilineInput,
                      {
                        backgroundColor: colors.inputBackground,
                        borderColor: colors.inputBorder,
                        color: colors.text,
                      },
                    ]}
                    multiline
                    numberOfLines={3}
                    value={cropsText}
                    onChangeText={setCropsText}
                    placeholderTextColor={colors.placeholder}
                  />

                  <View style={styles.formRow}>
                    <View style={{ flex: 1 }}>
                      <ThemedText style={styles.fieldLabel}>Start Date</ThemedText>
                      <TextInput
                        style={[
                          styles.input,
                          {
                            backgroundColor: colors.inputBackground,
                            borderColor: colors.inputBorder,
                            color: colors.text,
                          },
                        ]}
                        value={startDate}
                        onChangeText={setStartDate}
                        placeholder="YYYY-MM-DD"
                        placeholderTextColor={colors.placeholder}
                      />
                    </View>
                    <View style={{ flex: 1, marginLeft: Spacing.two }}>
                      <ThemedText style={styles.fieldLabel}>Harvest Interval (Days)</ThemedText>
                      <TextInput
                        style={[
                          styles.input,
                          {
                            backgroundColor: colors.inputBackground,
                            borderColor: colors.inputBorder,
                            color: colors.text,
                          },
                        ]}
                        value={harvestInterval}
                        onChangeText={setHarvestInterval}
                        keyboardType="number-pad"
                        placeholderTextColor={colors.placeholder}
                      />
                    </View>
                  </View>

                  <View style={styles.formRow}>
                    <View style={{ flex: 1 }}>
                      <ThemedText style={styles.fieldLabel}>Harvest Batches</ThemedText>
                      <TextInput
                        style={[
                          styles.input,
                          {
                            backgroundColor: colors.inputBackground,
                            borderColor: colors.inputBorder,
                            color: colors.text,
                          },
                        ]}
                        value={batchesWanted}
                        onChangeText={setBatchesWanted}
                        keyboardType="number-pad"
                        placeholder="0 for auto"
                        placeholderTextColor={colors.placeholder}
                      />
                    </View>
                    <View style={{ flex: 1, marginLeft: Spacing.two }}>
                      <ThemedText style={styles.fieldLabel}>Variations per Group</ThemedText>
                      <TextInput
                        style={[
                          styles.input,
                          {
                            backgroundColor: colors.inputBackground,
                            borderColor: colors.inputBorder,
                            color: colors.text,
                          },
                        ]}
                        value={variationsPerGroup}
                        onChangeText={setVariationsPerGroup}
                        keyboardType="number-pad"
                        placeholder="2"
                        placeholderTextColor={colors.placeholder}
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
                </View>
              )}
            </View>
          </ScrollView>
        )}
      </SafeAreaView>

      {/* Add Section Modal */}
      <Modal
        visible={sectionModalVisible}
        animationType="slide"
        onRequestClose={() => setSectionModalVisible(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: colors.border }]}>
            <ThemedText type="subtitle">Create Farm Section</ThemedText>
            <TouchableOpacity onPress={() => setSectionModalVisible(false)} style={styles.closeHeaderBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <ThemedText style={[styles.closeHeaderText, { color: colors.textSecondary }]}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Section Name *</ThemedText>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.inputBackground,
                  borderColor: colors.inputBorder,
                  color: colors.text,
                },
              ]}
              placeholder="e.g. Bed A, Row 1, Greenhouse Shelf B"
              placeholderTextColor={colors.placeholder}
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
                    {
                      backgroundColor: secLocationId === loc.id ? colors.primary : colors.backgroundElement,
                      borderColor: secLocationId === loc.id ? colors.primary : colors.border,
                    },
                  ]}
                  onPress={() => setSecLocationId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      { color: secLocationId === loc.id ? colors.textInverse : colors.text },
                      secLocationId === loc.id && { fontWeight: 'bold' },
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
                    {
                      backgroundColor: secType === type ? colors.primary : colors.backgroundElement,
                      borderColor: secType === type ? colors.primary : colors.border,
                    },
                  ]}
                  onPress={() => setSecType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      { color: secType === type ? colors.textInverse : colors.text },
                      secType === type && { fontWeight: 'bold' },
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
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  value={secWidth}
                  onChangeText={setSecWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  value={secLength}
                  onChangeText={setSecLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <View style={styles.modalButtonGroup}>
              <TouchableOpacity
                style={[
                  styles.submitBtn,
                  styles.cancelBtn,
                  {
                    backgroundColor: colors.backgroundElement,
                    borderColor: colors.border,
                  },
                ]}
                onPress={() => setSectionModalVisible(false)}
                disabled={actionLoading}
              >
                <ThemedText style={[styles.cancelBtnText, { color: colors.text }]}>Cancel</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.submitBtn, styles.primarySubmitBtn, { backgroundColor: colors.primary }]}
                onPress={handleCreateSection}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <ThemedText style={[styles.submitBtnText, { color: colors.textInverse }]}>Create Section</ThemedText>
                )}
              </TouchableOpacity>
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Section Modal */}
      <Modal
        visible={editSectionModalVisible}
        animationType="slide"
        onRequestClose={() => setEditSectionModalVisible(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: colors.border }]}>
            <ThemedText type="subtitle">Edit Farm Section</ThemedText>
            <TouchableOpacity onPress={() => setEditSectionModalVisible(false)} style={styles.closeHeaderBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <ThemedText style={[styles.closeHeaderText, { color: colors.textSecondary }]}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Section Name *</ThemedText>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.inputBackground,
                  borderColor: colors.inputBorder,
                  color: colors.text,
                },
              ]}
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
                    {
                      backgroundColor: editSecLocationId === loc.id ? colors.primary : colors.backgroundElement,
                      borderColor: editSecLocationId === loc.id ? colors.primary : colors.border,
                    },
                  ]}
                  onPress={() => setEditSecLocationId(loc.id)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      { color: editSecLocationId === loc.id ? colors.textInverse : colors.text },
                      editSecLocationId === loc.id && { fontWeight: 'bold' },
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
                    {
                      backgroundColor: editSecType === type ? colors.primary : colors.backgroundElement,
                      borderColor: editSecType === type ? colors.primary : colors.border,
                    },
                  ]}
                  onPress={() => setEditSecType(type)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      { color: editSecType === type ? colors.textInverse : colors.text },
                      editSecType === type && { fontWeight: 'bold' },
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
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  value={editSecWidth}
                  onChangeText={setEditSecWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  value={editSecLength}
                  onChangeText={setEditSecLength}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <View style={styles.modalButtonGroup}>
              <TouchableOpacity
                style={[
                  styles.submitBtn,
                  styles.cancelBtn,
                  {
                    backgroundColor: colors.backgroundElement,
                    borderColor: colors.border,
                  },
                ]}
                onPress={() => setEditSectionModalVisible(false)}
                disabled={actionLoading}
              >
                <ThemedText style={[styles.cancelBtnText, { color: colors.text }]}>Cancel</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.submitBtn, styles.primarySubmitBtn, { backgroundColor: colors.primary }]}
                onPress={handleUpdateSection}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <ThemedText style={[styles.submitBtnText, { color: colors.textInverse }]}>Save Changes</ThemedText>
                )}
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[
                styles.submitBtn,
                styles.deleteBtn,
                { backgroundColor: colors.errorBackground, borderColor: colors.error },
              ]}
              onPress={() => handleDeleteSection(selectedSection.id, selectedSection.name)}
              disabled={actionLoading}
            >
              <ThemedText style={[styles.submitBtnText, { color: colors.errorText }]}>Delete Section</ThemedText>
            </TouchableOpacity>
          </ScrollView>
        </SafeAreaView>
      </Modal>

      {/* Edit Location Modal */}
      <Modal
        visible={editLocModalVisible}
        animationType="slide"
        onRequestClose={() => setEditLocModalVisible(false)}
      >
        <SafeAreaView style={[styles.modalContainer, { backgroundColor: colors.background }]}>
          <View style={[styles.modalHeader, { borderBottomColor: colors.border }]}>
            <ThemedText type="subtitle">Edit Location</ThemedText>
            <TouchableOpacity onPress={() => setEditLocModalVisible(false)} style={styles.closeHeaderBtn} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
              <ThemedText style={[styles.closeHeaderText, { color: colors.textSecondary }]}>✕</ThemedText>
            </TouchableOpacity>
          </View>

          <ScrollView contentContainerStyle={styles.modalForm}>
            <ThemedText style={styles.fieldLabel}>Location Name *</ThemedText>
            <TextInput
              style={[
                styles.input,
                {
                  backgroundColor: colors.inputBackground,
                  borderColor: colors.inputBorder,
                  color: colors.text,
                },
              ]}
              value={editLocName}
              onChangeText={setEditLocName}
            />

            <ThemedText style={styles.fieldLabel}>Description</ThemedText>
            <TextInput
              style={[
                styles.input,
                { height: 80, paddingTop: 10 },
                {
                  backgroundColor: colors.inputBackground,
                  borderColor: colors.inputBorder,
                  color: colors.text,
                },
              ]}
              multiline
              numberOfLines={3}
              placeholder="e.g. Sunny east-facing balcony."
              placeholderTextColor={colors.placeholder}
              value={editLocDesc}
              onChangeText={setEditLocDesc}
            />

            <ThemedText style={styles.fieldLabel}>Environment</ThemedText>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.horizontalSelect}>
              {['outdoor', 'greenhouse', 'indoor', 'hydroponic'].map((env) => (
                <TouchableOpacity
                  key={env}
                  style={[
                    styles.typeOption,
                    {
                      backgroundColor: editLocEnv === env ? colors.primary : colors.backgroundElement,
                      borderColor: editLocEnv === env ? colors.primary : colors.border,
                    },
                  ]}
                  onPress={() => setEditLocEnv(env)}
                >
                  <ThemedText
                    style={[
                      styles.typeOptionText,
                      { color: editLocEnv === env ? colors.textInverse : colors.text },
                      editLocEnv === env && { fontWeight: 'bold' },
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
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  value={editLocWidth}
                  onChangeText={setEditLocWidth}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Length (meters)</ThemedText>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
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
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  placeholder="e.g. 37.7749"
                  placeholderTextColor={colors.placeholder}
                  value={editLocLat}
                  onChangeText={setEditLocLat}
                  keyboardType="numeric"
                />
              </View>
              <View style={{ flex: 1, marginLeft: Spacing.two }}>
                <ThemedText style={styles.fieldLabel}>Longitude (optional)</ThemedText>
                <TextInput
                  style={[
                    styles.input,
                    {
                      backgroundColor: colors.inputBackground,
                      borderColor: colors.inputBorder,
                      color: colors.text,
                    },
                  ]}
                  placeholder="e.g. -122.4194"
                  placeholderTextColor={colors.placeholder}
                  value={editLocLng}
                  onChangeText={setEditLocLng}
                  keyboardType="numeric"
                />
              </View>
            </View>

            <View style={styles.modalButtonGroup}>
              <TouchableOpacity
                style={[
                  styles.submitBtn,
                  styles.cancelBtn,
                  {
                    backgroundColor: colors.backgroundElement,
                    borderColor: colors.border,
                  },
                ]}
                onPress={() => setEditLocModalVisible(false)}
                disabled={actionLoading}
              >
                <ThemedText style={[styles.cancelBtnText, { color: colors.text }]}>Cancel</ThemedText>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.submitBtn, styles.primarySubmitBtn, { backgroundColor: colors.primary }]}
                onPress={handleUpdateLocation}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <ThemedText style={[styles.submitBtnText, { color: colors.textInverse }]}>Save Changes</ThemedText>
                )}
              </TouchableOpacity>
            </View>

            <TouchableOpacity
              style={[
                styles.submitBtn,
                styles.deleteBtn,
                { backgroundColor: colors.errorBackground, borderColor: colors.error },
              ]}
              onPress={() => selectedLoc && handleDeleteLocation(selectedLoc.id, selectedLoc.name)}
              disabled={actionLoading}
            >
              <ThemedText style={[styles.submitBtnText, { color: colors.errorText }]}>Delete Location</ThemedText>
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
  scrollContent: {
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
    borderWidth: 1,
  },
  typeOptionSelected: {},
  typeOptionText: {
    fontSize: 14,
  },
  input: {
    height: 48,
    borderWidth: 1,
    borderRadius: Spacing.two,
    paddingHorizontal: Spacing.three,
    marginBottom: Spacing.two,
    fontSize: 16,
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
    borderRadius: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.four,
    flexDirection: 'row',
  },
  submitBtnText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.four,
    borderBottomWidth: 1,
  },
  modalForm: {
    padding: Spacing.four,
  },
  deleteBtn: {
    marginTop: Spacing.two,
  },
  warnText: {
    fontSize: 12,
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
    borderWidth: 1,
    gap: Spacing.one,
  },
  secMultiBtnSelected: {},
  secMultiBtnText: {
    fontSize: 13,
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
    borderWidth: 1,
    flex: 1,
    marginTop: 0,
  },
  cancelBtnText: {
    fontSize: 16,
    fontWeight: '600',
  },
  closeHeaderBtn: {
    padding: Spacing.one,
  },
  closeHeaderText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  locationLinkBtn: {
    marginTop: 2,
    alignSelf: 'flex-start',
  },
  locNameHighlight: {
    fontWeight: '600',
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