import { motion } from 'framer-motion';
import React from 'react';

const Blob = ({ color, initialPos, duration }: { color: string, initialPos: any, duration: number }) => (
  <motion.div
    animate={{
      x: [0, 50, -50, 0],
      y: [0, 30, -30, 0],
      scale: [1, 1.2, 0.9, 1],
    }}
    transition={{
      duration: duration,
      repeat: Infinity,
      ease: "linear",
    }}
    style={{
      position: 'absolute',
      width: '40vw',
      height: '40vw',
      background: color,
      borderRadius: '50%',
      filter: 'blur(80px)',
      mixBlendMode: 'screen',
      ...initialPos,
    }}
  />
);

export const LavaLampBackground = React.memo(() => (
  <div style={{ position: 'fixed', inset: 0, overflow: 'hidden', zIndex: -1, background: '#0a0a0a' }}>
    <Blob color="#ff0080" initialPos={{ top: '-10%', left: '-10%' }} duration={25} />
    <Blob color="#7928ca" initialPos={{ bottom: '-10%', right: '-10%' }} duration={30} />
    <Blob color="#ff4d4d" initialPos={{ top: '20%', left: '40%' }} duration={20} />
  </div>
));
