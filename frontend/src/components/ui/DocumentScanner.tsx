import { motion } from 'framer-motion'

export default function DocumentScanner() {
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-xl">
      {/* The scanning line */}
      <motion.div
        initial={{ top: '-10%' }}
        animate={{ top: '110%' }}
        transition={{ 
          duration: 3, 
          repeat: Infinity, 
          ease: "linear" 
        }}
        className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-brand-400 to-transparent z-10"
      >
        {/* Glow effect */}
        <div className="absolute inset-0 bg-brand-400 blur-md opacity-50" />
      </motion.div>
      
      {/* Pulsing overlay */}
      <motion.div
        animate={{ opacity: [0.05, 0.15, 0.05] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="absolute inset-0 bg-brand-400 mix-blend-overlay"
      />
    </div>
  )
}
