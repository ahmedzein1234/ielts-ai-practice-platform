'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ProgressRingProps {
  progress: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  backgroundColor?: string;
  showPercentage?: boolean;
  className?: string;
}

export function ProgressRing({
  progress,
  size = 120,
  strokeWidth = 8,
  color = '#3B82F6',
  backgroundColor = '#E5E7EB',
  showPercentage = true,
  className,
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={backgroundColor}
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        
        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          strokeLinecap="round"
        />
      </svg>
      
      {showPercentage && (
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.span
            className="text-lg font-bold text-gray-900 dark:text-gray-100"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            {Math.round(progress)}%
          </motion.span>
        </div>
      )}
    </div>
  );
}

interface SkillProgressProps {
  skill: string;
  currentScore: number;
  targetScore: number;
  className?: string;
}

export function SkillProgress({ skill, currentScore, targetScore, className }: SkillProgressProps) {
  const progress = (currentScore / targetScore) * 100;
  const isAchieved = currentScore >= targetScore;

  return (
    <div className={cn('flex items-center space-x-4 p-4 rounded-lg border', className)}>
      <ProgressRing
        progress={Math.min(progress, 100)}
        size={60}
        strokeWidth={6}
        color={isAchieved ? '#10B981' : '#3B82F6'}
        showPercentage={false}
      />
      
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="font-medium text-sm capitalize">{skill}</span>
          <span className="text-xs text-muted-foreground">
            {currentScore.toFixed(1)} / {targetScore.toFixed(1)}
          </span>
        </div>
        
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <motion.div
            className={cn(
              'h-2 rounded-full transition-colors duration-300',
              isAchieved ? 'bg-green-500' : 'bg-blue-500'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(progress, 100)}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        </div>
      </div>
    </div>
  );
}
