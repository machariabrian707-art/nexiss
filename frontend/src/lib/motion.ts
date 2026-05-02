import type { Variants } from 'framer-motion'

export const motionTokens = {
  duration: {
    fast: 0.22,
    base: 0.42,
    slow: 1.0,
  },
  ease: {
    standard: [0.4, 0, 0.2, 1] as const,
    entrance: [0.2, 0.8, 0.2, 1] as const,
    exit: 'easeIn' as const,
  },
}

export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.04,
    },
  },
}

export const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20, scale: 0.96 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: motionTokens.duration.base,
      ease: motionTokens.ease.entrance,
    },
  },
  hover: {
    scale: 1.03,
    rotateX: 4,
    boxShadow: '0px 18px 45px rgba(0, 0, 0, 0.35)',
    transition: {
      duration: motionTokens.duration.fast,
      ease: motionTokens.ease.standard,
    },
  },
}
