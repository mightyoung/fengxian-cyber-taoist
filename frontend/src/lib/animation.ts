/**
 * FengxianCyberTaoist Animation System
 * Framer Motion animation configurations
 */

export const ANIMATIONS = {
  micro: {
    duration: 150,
    easing: [0.4, 0, 0.2, 1] as const, // cubic-bezier(0.4, 0, 0.2, 1)
  },
  standard: {
    duration: 250,
    easing: [0.25, 0.46, 0.45, 0.94] as const, // ease-out-quart
  },
  slow: {
    duration: 400,
    easing: [0.16, 1, 0.3, 1] as const, // ease-out-expo
  },
  star: {
    duration: 2000,
    easing: [0.4, 0, 0.6, 1] as const, // ease-in-out
  },
} as const;

export const TRANSITIONS = {
  default: {
    type: 'tween',
    ease: ANIMATIONS.standard.easing,
    duration: ANIMATIONS.standard.duration,
  },
  spring: {
    type: 'spring',
    stiffness: 300,
    damping: 30,
  },
  gentle: {
    type: 'tween',
    ease: 'easeInOut',
    duration: ANIMATIONS.slow.duration,
  },
} as const;

export const FADE_IN_VARIANTS = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
} as const;

export const SLIDE_UP_VARIANTS = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
} as const;

export const SCALE_VARIANTS = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
} as const;
