import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Alert,
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

export default function PlanPreviewScreen() {
  const colors = useTheme();
  const router = useRouter();
  const { confirmPolyculture, getPolyculturePreview } = useData();

  const [loading, setLoading] = useState(true);
  const [payload, setPayload] = useState<any>(null);
  const [preview, setPreview] = useState<any>(null);
  const [planName, setPlanName] = useState('Polyculture Production Plan');
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [selectedAdditions, setSelectedAdditions] = useState<Record<number, string[]>>({});

  useEffect(() => {
    async function loadPreviewData() {
      try {
        const storedPayload = await AsyncStorage.getItem('pending_preview_payload');
        const storedResult = await AsyncStorage.getItem('pending_preview_result');
        if (storedPayload && storedResult) {
          setPayload(JSON.parse(storedPayload));
          setPreview(JSON.parse(storedResult));
        } else {
          Alert.alert('Error', 'No plan preview data found');
          router.back();
        }
      } catch (e) {
        Alert.alert('Error', 'Failed to load preview');
      } finally {
        setLoading(false);
      }
    }
    loadPreviewData();
  }, []);

  const handleRegenerate = async (groupId: number) => {
    const additions = selectedAdditions[groupId] || [];
    if (additions.length === 0) return;

    setConfirmLoading(true);
    try {
      // Merge additions into the intended crops list
      const currentCrops = payload.intended_crops || [];
      const updatedCrops = Array.from(new Set([...currentCrops, ...additions]));
      const updatedPayload = { ...payload, intended_crops: updatedCrops };

      const result = await getPolyculturePreview(updatedPayload);

      // Save updated data
      await AsyncStorage.setItem('pending_preview_payload', JSON.stringify(updatedPayload));
      await AsyncStorage.setItem('pending_preview_result', JSON.stringify(result));

      setPayload(updatedPayload);
      setPreview(result);
      setSelectedAdditions({ ...selectedAdditions, [groupId]: [] });
      Alert.alert('Success', 'Plan regenerated with new crops!');
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to regenerate plan');
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleConfirmPlan = async () => {
    if (!planName.trim()) {
      Alert.alert('Error', 'Plan name is required');
      return;
    }

    setConfirmLoading(true);
    try {
      const finalPayload = {
        ...payload,
        name: planName.trim(),
      };
      await confirmPolyculture(finalPayload);
      Alert.alert('Success', 'Polyculture plan confirmed and saved!', [
        { text: 'OK', onPress: () => router.replace('/planning') },
      ]);
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to confirm plan');
    } finally {
      setConfirmLoading(false);
    }
  };

  const toggleAdditionSelection = (groupId: number, plantName: string) => {
    const current = selectedAdditions[groupId] || [];
    if (current.includes(plantName)) {
      setSelectedAdditions({
        ...selectedAdditions,
        [groupId]: current.filter((x) => x !== plantName),
      });
    } else {
      setSelectedAdditions({
        ...selectedAdditions,
        [groupId]: [...current, plantName],
      });
    }
  };

  if (loading) {
    return (
      <ThemedView style={styles.center}>
        <ActivityIndicator size="large" color={colors.emerald} />
      </ThemedView>
    );
  }

  if (!preview) return null;

  const warnings = preview.warnings || [];
  const suggestedSections = preview.suggested_additional_sections || [];
  const groups = preview.groups || [];

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <SymbolView name="chevron.left" size={24} tintColor={colors.emerald} />
          </TouchableOpacity>
          <View>
            <ThemedText type="subtitle" style={styles.title}>
              Plan Preview
            </ThemedText>
            <ThemedText themeColor="textSecondary">
              Review generated planting groups
            </ThemedText>
          </View>
        </View>

        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Warnings Banner */}
          {warnings.length > 0 && (
            <ThemedView style={[styles.warningBanner, { backgroundColor: colors.badgeErrorBackground, borderColor: colors.badgeErrorText }]}>
              <View style={styles.warningTitleLine}>
                <SymbolView name="exclamationmark.triangle.fill" size={16} tintColor={colors.badgeErrorText} />
                <ThemedText style={[styles.warningTitle, { color: colors.badgeErrorText }]}>Planning Warnings</ThemedText>
              </View>
              {warnings.map((warn: string, i: number) => (
                <ThemedText key={`warn-${i}`} style={[styles.warningText, { color: colors.badgeErrorText }]}>
                  • {warn}
                </ThemedText>
              ))}
            </ThemedView>
          )}

          {/* Suggested Sections */}
          {suggestedSections.length > 0 && (
            <ThemedView style={[styles.suggestionBanner, { backgroundColor: colors.infoBackground, borderColor: colors.info }]}>
              <View style={styles.suggestionTitleLine}>
                <SymbolView name="info.circle.fill" size={16} tintColor={colors.info} />
                <ThemedText style={[styles.suggestionTitle, { color: colors.infoText }]}>Suggested Additional Sections</ThemedText>
              </View>
              {suggestedSections.map((sec: any, i: number) => (
                <ThemedText key={`sec-${i}`} style={styles.suggestionText}>
                  • {sec.name} ({sec.area_m2} m²)
                </ThemedText>
              ))}
            </ThemedView>
          )}

          {/* Vitals Summary */}
          <View style={styles.vitalsRow}>
            <ThemedView type="backgroundElement" style={styles.vitalCard}>
              <ThemedText themeColor="textSecondary" style={styles.vitalLabel}>
                Safe Groups
              </ThemedText>
              <ThemedText type="subtitle" style={styles.vitalValue}>
                {preview.group_count}
              </ThemedText>
            </ThemedView>
            <ThemedView type="backgroundElement" style={styles.vitalCard}>
              <ThemedText themeColor="textSecondary" style={styles.vitalLabel}>
                Total Area
              </ThemedText>
              <ThemedText type="subtitle" style={styles.vitalValue}>
                {preview.total_available_area_m2} m²
              </ThemedText>
            </ThemedView>
          </View>

          {/* Generated Groups */}
          <ThemedText type="smallBold" style={styles.sectionHeading}>
            Generated Planting Groups
          </ThemedText>

          {groups.map((group: any) => {
            const additions = selectedAdditions[group.group_id] || [];
            const recAdditions = group.recommended_additions || [];
            const remainingSlots = group.remaining_plant_slots;

            return (
              <ThemedView key={group.group_id} type="backgroundElement" style={styles.groupCard}>
                <ThemedText type="smallBold" style={styles.groupTitle}>
                  Group {group.group_id} - {group.section_name || 'Not assigned'}
                </ThemedText>
                <ThemedText type="small" themeColor="textSecondary">
                  Allocated area: {group.allocated_area_m2} m²
                </ThemedText>

                {/* Main crops */}
                <View style={styles.metaBlock}>
                  <ThemedText type="smallBold" style={styles.metaBlockTitle}>
                    Main Crops
                  </ThemedText>
                  <ThemedText style={styles.cropsList}>
                    {group.main_crops?.join(', ')}
                  </ThemedText>
                </View>

                {/* Suggested companions */}
                {group.suggested_companions?.length > 0 && (
                  <View style={styles.metaBlock}>
                    <ThemedText type="smallBold" style={styles.metaBlockTitle}>
                      Suggested Companions
                    </ThemedText>
                    {group.suggested_companions.map((comp: any, idx: number) => (
                      <ThemedText key={`comp-${idx}`} style={styles.companionRow}>
                        • {comp.plant} — {comp.description || 'Recommended companion'}
                      </ThemedText>
                    ))}
                  </View>
                )}

                {/* Timeline */}
                {group.timeline?.length > 0 && (
                  <View style={styles.metaBlock}>
                    <ThemedText type="smallBold" style={styles.metaBlockTitle}>
                      Timeline Steps
                    </ThemedText>
                    {group.timeline.map((step: any, idx: number) => (
                      <View key={`step-${idx}`} style={styles.timelineRow}>
                        <ThemedText style={styles.timelineLabel}>Batch {step.batch_number}:</ThemedText>
                        <ThemedText style={styles.timelineValue}>
                          {step.seed_start_date} (Seed) → {step.expected_harvest_date} (Harvest)
                        </ThemedText>
                      </View>
                    ))}
                  </View>
                )}

                {/* Layout preview grid */}
                {group.layout?.placements?.length > 0 && (
                  <View style={styles.metaBlock}>
                    <ThemedText type="smallBold" style={styles.metaBlockTitle}>
                      Grid Arrangement ({group.layout.grid_width}x{group.layout.grid_height})
                    </ThemedText>
                    <ScrollView horizontal contentContainerStyle={{ paddingVertical: Spacing.one }}>
                      <View style={styles.placementsGrid}>
                        {Array.from({ length: group.layout.grid_height }).map((_, y) => (
                          <View key={`row-${y}`} style={styles.placementsRow}>
                            {Array.from({ length: group.layout.grid_width }).map((_, x) => {
                              const cell = group.layout.placements.find(
                                (p: any) => p.x === x && p.y === y
                              );
                              return (
                                <View
                                  key={`cell-${x}-${y}`}
                                  style={[
                                    styles.placementCell,
                                    cell ? styles.placementCellOccupied : styles.placementCellEmpty,
                                  ]}
                                >
                                  {cell ? (
                                    <>
                                      <ThemedText style={styles.placementCellText} numberOfLines={1}>
                                        {cell.name}
                                      </ThemedText>
                                      <ThemedText style={styles.placementCellSub}>
                                        {`G${cell.group_id}`}
                                      </ThemedText>
                                    </>
                                  ) : (
                                    <ThemedText style={{ color: '#ccc' }}>-</ThemedText>
                                  )}
                                </View>
                              );
                            })}
                          </View>
                        ))}
                      </View>
                    </ScrollView>
                  </View>
                )}

                {/* Recommended Additions & Regenerate */}
                {recAdditions.length > 0 && (
                  <View style={styles.additionsSection}>
                    <ThemedText type="smallBold" style={styles.metaBlockTitle}>
                      Compatible Additions ({remainingSlots} slot(s) left)
                    </ThemedText>
                    <View style={styles.additionsList}>
                      {recAdditions.map((item: any) => {
                        const isChecked = additions.includes(item.plant);
                        return (
                          <TouchableOpacity
                            key={item.plant}
                            style={[
                              styles.additionOption,
                              isChecked && styles.additionOptionActive,
                            ]}
                            onPress={() => toggleAdditionSelection(group.group_id, item.plant)}
                          >
                            <SymbolView
                              name={isChecked ? 'checkmark.circle.fill' : 'circle'}
                              size={14}
                              tintColor={isChecked ? colors.textInverse : colors.emerald}
                            />
                            <ThemedText
                              style={[
                                styles.additionOptionText,
                                isChecked && { color: colors.textInverse, fontWeight: 'bold' },
                              ]}
                            >
                              {item.plant}
                            </ThemedText>
                          </TouchableOpacity>
                        );
                      })}
                    </View>

                    <TouchableOpacity
                      style={[styles.regenerateBtn, { backgroundColor: colors.blue }]}
                      onPress={() => handleRegenerate(group.group_id)}
                      disabled={additions.length === 0 || confirmLoading}
                    >
                      <SymbolView name="arrow.clockwise" size={12} tintColor={colors.textInverse} />
                      <ThemedText style={[styles.regenerateBtnText, { color: colors.textInverse }]}>Add & Regenerate</ThemedText>
                    </TouchableOpacity>
                  </View>
                )}
              </ThemedView>
            );
          })}

          {/* Confirm Plan Form */}
          <ThemedView type="backgroundElement" style={styles.confirmCard}>
            <ThemedText type="smallBold" style={styles.confirmCardTitle}>
              Confirm and Save Plan
            </ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, borderColor: colors.border }]}
              placeholder="e.g. Summer Tomato Plan"
              placeholderTextColor={colors.placeholder}
              value={planName}
              onChangeText={setPlanName}
            />

            <TouchableOpacity
              style={[styles.confirmBtn, { backgroundColor: colors.emerald }]}
              onPress={handleConfirmPlan}
              disabled={confirmLoading}
            >
              {confirmLoading ? (
                <ActivityIndicator color={colors.textInverse} />
              ) : (
                <>
                  <SymbolView name="checkmark.circle" size={16} tintColor={colors.textInverse} style={{ marginRight: 6 }} />
                  <ThemedText style={[styles.confirmBtnText, { color: colors.textInverse }]}>Save Polyculture Plan</ThemedText>
                </>
              )}
            </TouchableOpacity>
          </ThemedView>
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
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.three,
    paddingTop: Spacing.two,
    marginBottom: Spacing.three,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  backButton: {
    padding: Spacing.two,
    marginRight: Spacing.two,
  },
  title: {
    fontWeight: 'bold',
  },
  scrollContent: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  warningBanner: {
    backgroundColor: '#FEE2E2',
    borderWidth: 1,
    borderColor: '#FCA5A5',
    borderRadius: Spacing.two,
    padding: Spacing.three,
    marginBottom: Spacing.three,
  },
  warningTitleLine: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.one,
    gap: Spacing.one,
  },
  warningTitle: {
    fontWeight: 'bold',
    color: '#991B1B',
  },
  warningText: {
    fontSize: 12,
    color: '#991B1B',
  },
  suggestionBanner: {
    backgroundColor: '#DBEAFE',
    borderWidth: 1,
    borderColor: '#93C5FD',
    borderRadius: Spacing.two,
    padding: Spacing.three,
    marginBottom: Spacing.three,
  },
  suggestionTitleLine: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.one,
    gap: Spacing.one,
  },
  suggestionTitle: {
    fontWeight: 'bold',
    color: '#1E40AF',
  },
  suggestionText: {
    fontSize: 12,
    color: '#1E40AF',
  },
  vitalsRow: {
    flexDirection: 'row',
    gap: Spacing.two,
    marginBottom: Spacing.four,
  },
  vitalCard: {
    flex: 1,
    padding: Spacing.three,
    borderRadius: Spacing.three,
    alignItems: 'center',
  },
  vitalLabel: {
    fontSize: 12,
  },
  vitalValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: 4,
  },
  sectionHeading: {
    fontSize: 18,
    marginBottom: Spacing.two,
  },
  groupCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.three,
  },
  groupTitle: {
    fontSize: 16,
    marginBottom: 2,
  },
  metaBlock: {
    marginTop: Spacing.two,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
    paddingTop: Spacing.two,
  },
  metaBlockTitle: {
    fontSize: 12,
    marginBottom: 4,
  },
  cropsList: {
    fontSize: 13,
  },
  companionRow: {
    fontSize: 12,
    marginTop: 2,
  },
  timelineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 2,
  },
  timelineLabel: {
    fontSize: 11,
    fontWeight: 'bold',
  },
  timelineValue: {
    fontSize: 11,
  },
  placementsGrid: {
    padding: Spacing.one,
    backgroundColor: 'rgba(0,0,0,0.03)',
    borderRadius: Spacing.two,
    gap: Spacing.half,
  },
  placementsRow: {
    flexDirection: 'row',
    gap: Spacing.half,
  },
  placementCell: {
    width: 60,
    height: 60,
    borderRadius: Spacing.one,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 2,
  },
  placementCellOccupied: {
    backgroundColor: 'rgba(16, 185, 129, 0.15)',
    borderWidth: 1,
    borderColor: '#10B981',
  },
  placementCellEmpty: {
    backgroundColor: 'rgba(0,0,0,0.05)',
  },
  placementCellText: {
    fontSize: 9,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  placementCellSub: {
    fontSize: 7,
    color: '#666',
  },
  additionsSection: {
    marginTop: Spacing.three,
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.08)',
    paddingTop: Spacing.two,
  },
  additionsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: Spacing.one,
    marginTop: Spacing.one,
  },
  additionOption: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    borderWidth: 1,
    borderColor: '#A7F3D0',
    paddingVertical: Spacing.one,
    paddingHorizontal: Spacing.two,
    borderRadius: Spacing.one,
    gap: Spacing.half,
  },
  additionOptionActive: {
    backgroundColor: '#10B981',
    borderColor: '#10B981',
  },
  additionOptionText: {
    fontSize: 11,
    color: '#065F46',
  },
  regenerateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#3B82F6',
    alignSelf: 'flex-start',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.two,
    marginTop: Spacing.two,
    gap: Spacing.one,
  },
  regenerateBtnText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  confirmCard: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginTop: Spacing.two,
  },
  confirmCardTitle: {
    fontSize: 16,
    marginBottom: Spacing.two,
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
  confirmBtn: {
    height: 48,
    backgroundColor: '#10B981',
    borderRadius: Spacing.two,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: Spacing.two,
    flexDirection: 'row',
  },
  confirmBtnText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
