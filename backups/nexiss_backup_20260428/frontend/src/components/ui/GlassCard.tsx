import React from 'react'
import clsx from 'clsx'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  title?: string
  subtitle?: string
  action?: React.ReactNode
  noPadding?: boolean
}

export default function GlassCard({
  children,
  className,
  title,
  subtitle,
  action,
  noPadding = false
}: GlassCardProps) {
  return (
    <div className={clsx('card group', className)}>
      {(title || action) && (
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-white/2">
          <div>
            {title && <h3 className="text-sm font-bold text-white font-lexend uppercase tracking-wider">{title}</h3>}
            {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className={clsx(noPadding ? '' : 'p-6')}>
        {children}
      </div>
      
      {/* Subtle glow on hover */}
      <div className="absolute inset-0 pointer-events-none border-2 border-transparent group-hover:border-brand-400/10 rounded-2xl transition-all duration-500" />
    </div>
  )
}
