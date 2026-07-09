import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { useAuth } from './AuthContext';

interface DataContextType {
  plants: any[];
  locations: any[];
  notifications: any[];
  needsWater: any[];
  sections: any[];
  savedPlans: any[];
  recommendations: any | null;
  loading: boolean;
  refreshing: boolean;
  
  refreshAll: () => Promise<void>;
  
  // Plant Actions
  addPlant: (payload: any, speciesId?: number) => Promise<any>;
  editPlant: (plantId: number, payload: any) => Promise<any>;
  removePlant: (plantId: number) => Promise<void>;
  dupPlant: (plantId: number) => Promise<any>;
  
  // Irrigation Actions
  waterOne: (plantId: number) => Promise<void>;
  waterAll: () => Promise<any>;
  
  // Location Actions
  addLocation: (payload: any) => Promise<any>;
  editLocation: (locationId: number, payload: any) => Promise<any>;
  removeLocation: (locationId: number) => Promise<void>;
  
  // Section Actions
  addSection: (payload: any) => Promise<any>;
  editSection: (sectionId: number, payload: any) => Promise<any>;
  removeSection: (sectionId: number) => Promise<void>;
  
  // Polyculture & Recommendations
  runRecommendations: () => Promise<any>;
  clearRecommendations: () => void;
  getPolyculturePreview: (payload: any) => Promise<any>;
  confirmPolyculture: (payload: any) => Promise<any>;
  removePolyculturePlan: (planId: number) => Promise<void>;
  
  // Notification Actions
  readNotification: (notificationId: number) => Promise<void>;
  
  // Species API Helper
  searchSpecies: (query: string) => Promise<any[]>;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export function DataProvider({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  
  const [plants, setPlants] = useState<any[]>([]);
  const [locations, setLocations] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [needsWater, setNeedsWater] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [savedPlans, setSavedPlans] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAllData = async (showRefreshIndicator = false) => {
    if (!token) return;
    if (showRefreshIndicator) setRefreshing(true);
    else setLoading(true);
    
    try {
      const [
        fetchedPlants,
        fetchedLocations,
        fetchedNotifications,
        fetchedNeedsWater,
        fetchedSections,
        fetchedPlans
      ] = await Promise.all([
        apiRequest('/plants/'),
        apiRequest('/locations/'),
        apiRequest('/notifications/'),
        apiRequest('/irrigation/needs-water'),
        apiRequest('/planning/sections'),
        apiRequest('/planning/polyculture-plans')
      ]);

      setPlants(fetchedPlants || []);
      setLocations(fetchedLocations || []);
      setNotifications(fetchedNotifications || []);
      setNeedsWater(fetchedNeedsWater || []);
      setSections(fetchedSections || []);
      setSavedPlans(fetchedPlans || []);
    } catch (e) {
      console.error('Failed to fetch smart farming data', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchAllData();
    } else {
      // Clear data on sign out
      setPlants([]);
      setLocations([]);
      setNotifications([]);
      setNeedsWater([]);
      setSections([]);
      setSavedPlans([]);
      setRecommendations(null);
    }
  }, [token]);

  const refreshAll = async () => {
    await fetchAllData(true);
  };

  // Plant Actions
  const addPlant = async (payload: any, speciesId?: number) => {
    let result;
    if (speciesId) {
      result = await apiRequest('/plants/with-species', {
        method: 'POST',
        params: { species_id: speciesId },
        body: payload,
      });
    } else {
      result = await apiRequest('/plants/', {
        method: 'POST',
        body: payload,
      });
    }
    setRecommendations(null); // invalidate recommendations
    await fetchAllData();
    return result;
  };

  const editPlant = async (plantId: number, payload: any) => {
    const result = await apiRequest(`/plants/${plantId}`, {
      method: 'PATCH',
      body: payload,
    });
    setRecommendations(null);
    await fetchAllData();
    return result;
  };

  const removePlant = async (plantId: number) => {
    await apiRequest(`/plants/${plantId}`, { method: 'DELETE' });
    setRecommendations(null);
    await fetchAllData();
  };

  const dupPlant = async (plantId: number) => {
    const result = await apiRequest(`/plants/${plantId}/duplicate`, { method: 'POST' });
    setRecommendations(null);
    await fetchAllData();
    return result;
  };

  // Irrigation Actions
  const waterOne = async (plantId: number) => {
    await apiRequest(`/irrigation/water/${plantId}`, { method: 'POST' });
    await fetchAllData();
  };

  const waterAll = async () => {
    const result = await apiRequest('/irrigation/water-all', { method: 'POST' });
    await fetchAllData();
    return result;
  };

  // Location Actions
  const addLocation = async (payload: any) => {
    const result = await apiRequest('/locations/', {
      method: 'POST',
      body: payload,
    });
    await fetchAllData();
    return result;
  };

  const editLocation = async (locationId: number, payload: any) => {
    const result = await apiRequest(`/locations/${locationId}`, {
      method: 'PATCH',
      body: payload,
    });
    await fetchAllData();
    return result;
  };

  const removeLocation = async (locationId: number) => {
    await apiRequest(`/locations/${locationId}`, { method: 'DELETE' });
    await fetchAllData();
  };

  // Section Actions
  const addSection = async (payload: any) => {
    const result = await apiRequest('/planning/sections', {
      method: 'POST',
      body: payload,
    });
    await fetchAllData();
    return result;
  };

  const editSection = async (sectionId: number, payload: any) => {
    const result = await apiRequest(`/planning/sections/${sectionId}`, {
      method: 'PATCH',
      body: payload,
    });
    await fetchAllData();
    return result;
  };

  const removeSection = async (sectionId: number) => {
    await apiRequest(`/planning/sections/${sectionId}`, { method: 'DELETE' });
    await fetchAllData();
  };

  // Recommendations
  const runRecommendations = async () => {
    const result = await apiRequest('/plants/recommendations');
    setRecommendations(result);
    return result;
  };

  const clearRecommendations = () => {
    setRecommendations(null);
  };

  // Polyculture previews & confirms
  const getPolyculturePreview = async (payload: any) => {
    return await apiRequest('/planning/polyculture-preview', {
      method: 'POST',
      body: payload,
    });
  };

  const confirmPolyculture = async (payload: any) => {
    const result = await apiRequest('/planning/polyculture-confirm', {
      method: 'POST',
      body: payload,
    });
    await fetchAllData();
    return result;
  };

  const removePolyculturePlan = async (planId: number) => {
    await apiRequest(`/planning/polyculture-plans/${planId}`, { method: 'DELETE' });
    await fetchAllData();
  };

  // Notification Actions
  const readNotification = async (notificationId: number) => {
    await apiRequest(`/notifications/${notificationId}/read`, { method: 'PUT' });
    await fetchAllData();
  };

  // Species Search API Helper
  const searchSpecies = async (query: string) => {
    return await apiRequest('/species/suggest', {
      params: { query },
      auth: false,
    });
  };

  return (
    <DataContext.Provider
      value={{
        plants,
        locations,
        notifications,
        needsWater,
        sections,
        savedPlans,
        recommendations,
        loading,
        refreshing,
        refreshAll,
        addPlant,
        editPlant,
        removePlant,
        dupPlant,
        waterOne,
        waterAll,
        addLocation,
        editLocation,
        removeLocation,
        addSection,
        editSection,
        removeSection,
        runRecommendations,
        clearRecommendations,
        getPolyculturePreview,
        confirmPolyculture,
        removePolyculturePlan,
        readNotification,
        searchSpecies,
      }}
    >
      {children}
    </DataContext.Provider>
  );
}

export function useData() {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error('useData must be used within a DataProvider');
  }
  return context;
}
