import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  TextInput,
  Image,
  Clipboard,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SymbolView } from 'expo-symbols';
import { useRouter } from 'expo-router';
import { useData } from '@/context/DataContext';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Spacing, BottomTabInset, MaxContentWidth } from '@/constants/theme';

export default function SpeciesSearchScreen() {
  const router = useRouter();
  const { searchSpecies } = useData();
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await searchSpecies(query.trim());
      setResults(data || []);
    } catch (e: any) {
      Alert.alert('Error', e.message || 'Failed to search species');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSpecies = (speciesId: number, commonName: string) => {
    Clipboard.setString(String(speciesId));
    Alert.alert(
      'Species Selected',
      `Species ID "${speciesId}" (${commonName}) has been copied to your clipboard! You can now paste this into the Perenual Species ID field.`,
      [{ text: 'Go Back', onPress: () => router.back() }, { text: 'Stay' }]
    );
  };

  return (
    <ThemedView style={styles.container}>
      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <SymbolView name="chevron.left" size={24} tintColor="#10B981" />
          </TouchableOpacity>
          <ThemedText type="subtitle" style={styles.title}>
            Species Lookup
          </ThemedText>
        </View>

        {/* Input */}
        <View style={styles.searchBar}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search by common or scientific name..."
            placeholderTextColor="#888"
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={handleSearch}
            autoCapitalize="none"
          />
          <TouchableOpacity style={styles.searchBtn} onPress={handleSearch}>
            <SymbolView name="magnifyingglass" size={18} tintColor="#fff" />
          </TouchableOpacity>
        </View>

        {/* Results */}
        {loading ? (
          <View style={styles.center}>
            <ActivityIndicator size="large" color="#10B981" />
          </View>
        ) : results.length === 0 ? (
          <View style={styles.empty}>
            <SymbolView name="magnifyingglass" size={48} tintColor="#ccc" />
            <ThemedText themeColor="textSecondary" style={styles.emptyText}>
              {query ? 'No species matches found.' : 'Enter a query to search Perenual API.'}
            </ThemedText>
          </View>
        ) : (
          <ScrollView contentContainerStyle={styles.list}>
            {results.map((species) => (
              <ThemedView key={species.id} type="backgroundElement" style={styles.card}>
                <View style={styles.cardHeader}>
                  {/* Image */}
                  {species.thumbnail_url ? (
                    <Image source={{ uri: species.thumbnail_url }} style={styles.thumbnail} />
                  ) : (
                    <View style={styles.noImage}>
                      <SymbolView name="photo" size={20} tintColor="#888" />
                    </View>
                  )}

                  {/* Info */}
                  <View style={styles.info}>
                    <ThemedText type="smallBold" style={styles.commonName}>
                      {species.common_name || 'Unknown'}
                    </ThemedText>
                    <ThemedText themeColor="textSecondary" style={styles.sciName}>
                      {species.scientific_name || 'Unknown scientific name'}
                    </ThemedText>
                    
                    <View style={styles.badgeRow}>
                      <View style={styles.badge}>
                        <ThemedText style={styles.badgeText}>{species.source || 'perenual'}</ThemedText>
                      </View>
                      <View style={[styles.badge, { backgroundColor: 'rgba(59, 130, 246, 0.1)' }]}>
                        <ThemedText style={styles.badgeText}>score {species.score?.toFixed(1) || '0.0'}</ThemedText>
                      </View>
                      <View style={[styles.badge, { backgroundColor: 'rgba(139, 92, 246, 0.1)' }]}>
                        <ThemedText style={styles.badgeText}>{species.plant_type || 'unknown'}</ThemedText>
                      </View>
                    </View>
                  </View>
                </View>

                {/* ID & Select action */}
                <View style={styles.actionRow}>
                  <ThemedText type="code" style={styles.speciesId}>
                    ID: {species.id}
                  </ThemedText>
                  <TouchableOpacity
                    style={styles.selectBtn}
                    onPress={() => handleSelectSpecies(species.id, species.common_name || 'Selected Species')}
                  >
                    <ThemedText style={styles.selectBtnText}>Copy ID & Apply</ThemedText>
                  </TouchableOpacity>
                </View>
              </ThemedView>
            ))}
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
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    marginHorizontal: Spacing.three,
    marginBottom: Spacing.four,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: Spacing.two,
    backgroundColor: '#fff',
    overflow: 'hidden',
    height: 48,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '90%',
  },
  searchInput: {
    flex: 1,
    paddingHorizontal: Spacing.three,
    fontSize: 16,
    color: '#000',
  },
  searchBtn: {
    width: 48,
    height: 48,
    backgroundColor: '#10B981',
    justifyContent: 'center',
    alignItems: 'center',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  empty: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.five,
  },
  emptyText: {
    fontSize: 14,
    marginTop: Spacing.two,
    textAlign: 'center',
  },
  list: {
    paddingHorizontal: Spacing.three,
    paddingBottom: BottomTabInset + Spacing.four,
    maxWidth: MaxContentWidth,
    alignSelf: 'center',
    width: '100%',
  },
  card: {
    padding: Spacing.three,
    borderRadius: Spacing.three,
    marginBottom: Spacing.three,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: Spacing.three,
  },
  thumbnail: {
    width: 70,
    height: 70,
    borderRadius: Spacing.two,
    backgroundColor: '#eee',
  },
  noImage: {
    width: 70,
    height: 70,
    borderRadius: Spacing.two,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  info: {
    flex: 1,
    justifyContent: 'center',
  },
  commonName: {
    fontSize: 16,
  },
  sciName: {
    fontSize: 12,
    fontStyle: 'italic',
    marginTop: 2,
    marginBottom: 6,
  },
  badgeRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 4,
  },
  badge: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    paddingVertical: 2,
    paddingHorizontal: 6,
    borderRadius: 6,
  },
  badgeText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#374151',
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: 'rgba(0,0,0,0.05)',
    marginTop: Spacing.two,
    paddingTop: Spacing.two,
  },
  speciesId: {
    fontSize: 13,
  },
  selectBtn: {
    backgroundColor: '#10B981',
    paddingVertical: Spacing.two,
    paddingHorizontal: Spacing.three,
    borderRadius: Spacing.one,
  },
  selectBtnText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
});
