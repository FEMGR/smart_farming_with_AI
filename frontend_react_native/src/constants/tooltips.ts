/**
 * Centralized configuration registry for UI tooltips and note descriptions.
 * Modify or add notes here to automatically update tooltips across the application.
 */

export const TOOLTIP_NOTES = {
  // Navigation & Header Actions
  signOut: 'Sign out',
  refreshData: 'Refresh',

  // Location Actions
  addLocation: 'Create',
  editLocation: 'Edit',
  useGps: 'GPS',

  // Plant Actions
  addPlant: 'Add New',
  editPlant: 'Edit',
  waterAll: 'Mark all',
  waterOne: 'Mark',
  searchSpecies: 'Lookup',

  // Planning & Sections
  addSection: 'Create',
  generatePlan: 'Generate',
  savePlan: 'Save',

  // Configuration & Settings
  apiConfig: 'Configure',
  themeToggle: 'Switch',
} as const;

export type TooltipKey = keyof typeof TOOLTIP_NOTES;

export default TOOLTIP_NOTES;
