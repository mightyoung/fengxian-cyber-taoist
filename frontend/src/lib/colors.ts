/**
 * FengxianCyberTaoist Color System
 * Eastern aesthetics with ink blue (#0F172A) and gold (#D4AF37) accents
 */

export const COLORS = {
  // Primary - Deep ink blue
  primary: {
    50: '#f0f4f8',
    100: '#d9e2ec',
    200: '#bcccdc',
    300: '#9fb3c8',
    400: '#829ab1',
    500: '#627d98',
    600: '#486581',
    700: '#334e68',
    800: '#243b53', // Dark background
    900: '#0F172A', // Deepest background (墨蓝)
    950: '#020617', // Near black
  },

  // Accent - Gold (金色)
  accent: {
    DEFAULT: '#D4AF37',
    light: '#F5D77A',
    dark: '#B8960C',
    glow: 'rgba(212, 175, 55, 0.3)',
  },

  // Star colors (星曜色彩)
  stars: {
    紫微: '#8B5CF6', // Purple - Emperor star
    天机: '#3B82F6', // Blue - Wisdom star
    太阳: '#F59E0B', // Orange-gold - Light star
    武曲: '#10B981', // Green
    天同: '#EC4899', // Pink
    廉贞: '#EF4444', // Red
    天府: '#D4AF37', // Gold
    太阴: '#6366F1', // Indigo
    贪狼: '#F97316', // Orange
    巨门: '#78716C', // Gray
    天相: '#14B8A6', // Teal
    天梁: '#84CC16', // Yellow-green
    七杀: '#DC2626', // Dark red
    破军: '#7C3AED', // Purple-red
  },

  // Semantic colors
  semantic: {
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
  },

  // Five elements (五行)
  wuxing: {
    木: '#22C55E', // Wood - Green
    火: '#EF4444', // Fire - Red
    土: '#D4AF37', // Earth - Gold
    金: '#F5F5F4', // Metal - White
    水: '#3B82F6', // Water - Blue
  },
} as const;

export type PrimaryColor = keyof typeof COLORS.primary;
export type AccentColor = keyof typeof COLORS.accent;
export type StarColor = keyof typeof COLORS.stars;
export type SemanticColor = keyof typeof COLORS.semantic;
export type WuxingColor = keyof typeof COLORS.wuxing;
