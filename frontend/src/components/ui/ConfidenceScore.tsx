import clsx from 'clsx'

interface ConfidenceScoreProps {
  score: number // 0 to 1
  showLabel?: boolean
}

export default function ConfidenceScore({ score, showLabel = true }: ConfidenceScoreProps) {
  const percentage = Math.round(score * 100)
  
  // 5 bars
  const bars = [0.2, 0.4, 0.6, 0.8, 1.0]
  
  const getColorClass = () => {
    if (score >= 0.9) return 'bg-emerald-400'
    if (score >= 0.7) return 'bg-brand-400'
    if (score >= 0.5) return 'bg-amber-400'
    return 'bg-rose-400'
  }

  const getTextColorClass = () => {
    if (score >= 0.9) return 'text-emerald-400'
    if (score >= 0.7) return 'text-brand-400'
    if (score >= 0.5) return 'text-amber-400'
    return 'text-rose-400'
  }

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-end gap-0.5 h-3">
        {bars.map((threshold, i) => (
          <div
            key={i}
            className={clsx(
              'w-1 rounded-full transition-all duration-500',
              score >= threshold ? getColorClass() : 'bg-white/10',
              // Dynamic height
              i === 0 && 'h-1.5',
              i === 1 && 'h-2',
              i === 2 && 'h-2.5',
              i === 3 && 'h-3',
              i === 4 && 'h-3.5'
            )}
          />
        ))}
      </div>
      {showLabel && (
        <span className={clsx('text-[10px] font-mono font-bold uppercase tracking-tighter', getTextColorClass())}>
          {percentage}% Confidence
        </span>
      )}
    </div>
  )
}
