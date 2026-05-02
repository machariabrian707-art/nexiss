import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'
import React, { useEffect } from 'react'

const Blob = ({ color, initialPos, duration }: { color: string; initialPos: React.CSSProperties; duration: number }) => (
  <motion.div
    animate={{
      x: [0, 50, -50, 0],
      y: [0, 30, -30, 0],
      scale: [1, 1.2, 0.9, 1],
    }}
    transition={{
      duration,
      repeat: Infinity,
      ease: 'linear',
    }}
    style={{
      position: 'absolute',
      width: '40vw',
      height: '40vw',
      background: color,
      borderRadius: '50%',
      filter: 'blur(80px)',
      mixBlendMode: 'screen',
      willChange: 'transform, opacity',
      ...initialPos,
    }}
  />
)

export const LavaLampBackground = React.memo(() => {
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const springX = useSpring(mouseX, { stiffness: 80, damping: 20 })
  const springY = useSpring(mouseY, { stiffness: 80, damping: 20 })
  const parallaxX = useTransform(springX, [-1, 1], [-12, 12])
  const parallaxY = useTransform(springY, [-1, 1], [-12, 12])

  useEffect(() => {
    const onMove = (event: MouseEvent) => {
      const x = event.clientX / window.innerWidth
      const y = event.clientY / window.innerHeight
      mouseX.set(x * 2 - 1)
      mouseY.set(y * 2 - 1)
    }

    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [mouseX, mouseY])

  return (
    <motion.div
      style={{
        position: 'fixed',
        inset: 0,
        overflow: 'hidden',
        zIndex: 0,
        pointerEvents: 'none',
        x: parallaxX,
        y: parallaxY,
        willChange: 'transform, opacity',
        background: 'linear-gradient(120deg, #06080f, #0f1631, #240f3d, #101a33)',
        backgroundSize: '240% 240%',
      }}
      animate={{ backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] }}
      transition={{ duration: 16, repeat: Infinity, ease: 'linear' }}
    >
      <Blob color="#ff0080" initialPos={{ top: '-10%', left: '-10%' }} duration={25} />
      <Blob color="#7928ca" initialPos={{ bottom: '-10%', right: '-10%' }} duration={30} />
      <Blob color="#ff4d4d" initialPos={{ top: '20%', left: '40%' }} duration={20} />
    </motion.div>
  )
})
