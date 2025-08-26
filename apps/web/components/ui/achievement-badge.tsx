'use client';

import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Trophy, Star, Target, Zap } from 'lucide-react';

interface AchievementBadgeProps {
  type: 'trophy' | 'star' | 'target' | 'streak';
  title: string;
  description: string;
  progress?: number;
  maxProgress?: number;
  isUnlocked?: boolean;
  className?: string;
  onClick?: () => void;
}

const achievementConfig = {
  trophy: { icon: Trophy, color: 'text-yellow-500', bgColor: 'bg-yellow-100 dark:bg-yellow-900' },
  star: { icon: Star, color: 'text-blue-500', bgColor: 'bg-blue-100 dark:bg-blue-900' },
  target: { icon: Target, color: 'text-green-500', bgColor: 'bg-green-100 dark:bg-green-900' },
  streak: { icon: Zap, color: 'text-purple-500', bgColor: 'bg-purple-100 dark:bg-purple-900' },
};

export function AchievementBadge({
  type,
  title,
  description,
  progress = 0,
  maxProgress = 100,
  isUnlocked = false,
  className,
  onClick,
}: AchievementBadgeProps) {
  const config = achievementConfig[type];
  const Icon = config.icon;
  const progressPercentage = Math.min((progress / maxProgress) * 100, 100);

  return (
    <motion.div
      className={cn(
        'relative group cursor-pointer transition-all duration-300',
        isUnlocked ? 'opacity-100' : 'opacity-60',
        className
      )}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
    >
      <div className={cn(
        'p-4 rounded-lg border-2 transition-all duration-300',
        isUnlocked 
          ? 'border-yellow-300 bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20' 
          : 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800'
      )}>
        <div className="flex items-start space-x-3">
          <div className={cn(
            'w-12 h-12 rounded-full flex items-center justify-center transition-all duration-300',
            config.bgColor,
            isUnlocked ? 'scale-110' : 'scale-100'
          )}>
            <Icon className={cn('w-6 h-6', config.color)} />
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className={cn(
              'font-semibold text-sm transition-colors duration-300',
              isUnlocked ? 'text-gray-900 dark:text-gray-100' : 'text-gray-600 dark:text-gray-400'
            )}>
              {title}
            </h3>
            <p className="text-xs text-muted-foreground mt-1">
              {description}
            </p>
            
            {!isUnlocked && maxProgress > 0 && (
              <div className="mt-2">
                <div className="flex justify-between text-xs text-muted-foreground mb-1">
                  <span>Progress</span>
                  <span>{progress}/{maxProgress}</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5">
                  <motion.div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progressPercentage}%` }}
                    transition={{ duration: 0.5, ease: 'easeOut' }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
        
        {isUnlocked && (
          <motion.div
            className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center"
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.3, ease: 'backOut' }}
          >
            <Star className="w-3 h-3 text-white fill-current" />
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
