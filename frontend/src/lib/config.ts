/**
 * FengxianCyberTaoist Configuration
 * Centralized configuration for all modules
 */

import { SimulationStatus } from '@/types/api';

export const BIRTH_CHART_CONFIG = {
  PALACE_COUNT: 12,
  MAIN_STARS_COUNT: 14,
  TRANSFORM_TYPES: ['化禄', '化权', '化科', '化忌'] as const,
  PALACE_NAMES: [
    '命宫', '父母宫', '兄弟宫', '夫妻宫',
    '子女宫', '财帛宫', '疾厄宫', '迁移宫',
    '奴仆宫', '事业宫', '田宅宫', '福德宫'
  ] as const,
} as const;

export const SIMULATION_CONFIG = {
  PLATFORMS: ['twitter', 'reddit'] as const,
  // Re-export SimulationStatus for convenience (imported from types/api.ts)
  STATUS: SimulationStatus,
  REFRESH_INTERVAL: 3000,
} as const;

export const UI_CONFIG = {
  ANIMATION_DURATION: 200,
  DEBOUNCE_DELAY: 300,
  TOAST_DURATION: 5000,
} as const;

export const GRAPH_CONFIG = {
  NODE_TYPES: {
    PERSON: 'person',
    ORGANIZATION: 'organization',
    LOCATION: 'location',
    EVENT: 'event',
    CONCEPT: 'concept',
  } as const,
  DEFAULT_NODE_COLOR: '#0F172A',
  SELECTED_NODE_COLOR: '#D4AF37',
  EDGE_COLOR: '#486581',
  HIGHLIGHTED_EDGE_COLOR: '#D4AF37',
} as const;

export const REPORT_CONFIG = {
  SECTIONS: {
    EXECUTIVE_SUMMARY: 'executive_summary',
    DETAILED_ANALYSIS: 'detailed_analysis',
    RECOMMENDATIONS: 'recommendations',
  } as const,
  EXPORT_FORMATS: ['pdf', 'json', 'markdown'] as const,
} as const;
