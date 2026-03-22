/**
 * Birth Chart Type Definitions
 * Types for Ziwei Dou Shu (紫微斗数) birth chart visualization
 */

// Five Elements (五行)
export type Wuxing = '木' | '火' | '土' | '金' | '水';

// Transform types (四化)
export type TransformType = '化禄' | '化权' | '化科' | '化忌';

// Star level
export type StarLevel = 'major' | 'minor' | 'auxiliary';

// Individual star
export interface Star {
  name: string;
  wuxing: Wuxing;
  level: StarLevel;
}

// Transform (四化曜)
export interface Transform {
  type: TransformType;
  star: string;
  wuxing: Wuxing;
}

// Palace (宫位)
export interface Palace {
  id: string;
  name: string;           // e.g., "命宫", "父母宫"
  tiangan: string;        // Heavenly stem (天干), e.g., "庚辛"
  stars: Star[];
  transforms?: Transform[];
  daxian?: string;       // Major period (大限)
  liunian?: string;      // Yearly flow (流年)
}

// Birth chart input
export interface BirthChartInput {
  year: number;
  month: number;
  day: number;
  hour: number;          // 0-23
  gender: 'male' | 'female';
  birthHourType?: 'zi' | ' Chou' | 'yin' | 'mao' | 'chen' | 'si' | 'wu' | 'wei' | 'shen' | 'you' | 'xu' | 'hai';
}

// Complete birth chart
export interface BirthChart {
  id: string;
  input: BirthChartInput;
  palaces: Palace[];
  createdAt: string;
  analysis?: ChartAnalysis;
}

// Chart analysis
export interface ChartAnalysis {
  overall: string;
  palaces: Record<string, PalaceAnalysis>;
  stars: Record<string, StarAnalysis>;
  periods: PeriodAnalysis[];
}

// Palace analysis
export interface PalaceAnalysis {
  summary: string;
  strength: 'strong' | 'weak' | 'balanced';
  notableStars: string[];
}

// Star analysis
export interface StarAnalysis {
  meaning: string;
  traits: string[];
  compatibleStars: string[];
  conflictingStars: string[];
}

// Period analysis (大限流年)
export interface PeriodAnalysis {
  type: 'daxian' | 'liunian';
  startYear: number;
  endYear: number;
  palace: string;
  overview: string;
}

// Palace names in order (十二宫)
export const PALACE_NAMES = [
  '命宫',     // Life Palace
  '父母宫',   // Parents Palace
  '兄弟宫',   // Siblings Palace
  '夫妻宫',   // Spouse Palace
  '子女宫',   // Children Palace
  '财帛宫',   // Wealth Palace
  '疾厄宫',   // Health Palace
  '迁移宫',   // Migration Palace
  '仆役宫',   // Servants Palace
  '官禄宫',   // Career Palace
  '田宅宫',   // Property Palace
  '福德宫',   // Fortune Palace
] as const;

// Main stars (十四主星)
export const MAIN_STARS = [
  '紫微', '天机', '太阳', '武曲', '天同', '廉贞',
  '天府', '太阴', '贪狼', '巨门', '天相', '天梁',
  '七杀', '破军',
] as const;

// Transform star mappings
export const TRANSFORM_STAR_MAP: Record<TransformType, string> = {
  '化禄': '禄存',
  '化权': '化权',
  '化科': '化科',
  '化忌': '化忌',
};
