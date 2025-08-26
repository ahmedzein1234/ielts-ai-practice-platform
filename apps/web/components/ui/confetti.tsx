'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ConfettiProps {
  isActive: boolean;
  duration?: number;
  colors?: string[];
}

interface ConfettiPiece {
  id: number;
  x: number;
  y: number;
  rotation: number;
  scale: number;
  color: string;
}

export function Confetti({ isActive, duration = 3000, colors = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'] }: ConfettiProps) {
  const [pieces, setPieces] = useState<ConfettiPiece[]>([]);

  useEffect(() => {
    if (isActive) {
      const newPieces = Array.from({ length: 50 }, (_, i) => ({
        id: i,
        x: Math.random() * 100,
        y: -10,
        rotation: Math.random() * 360,
        scale: Math.random() * 0.5 + 0.5,
        color: colors[Math.floor(Math.random() * colors.length)],
      }));
      
      setPieces(newPieces);

      const timer = setTimeout(() => {
        setPieces([]);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isActive, duration, colors]);

  return (
    <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
      <AnimatePresence>
        {pieces.map((piece) => (
          <motion.div
            key={piece.id}
            className="absolute w-2 h-2 rounded-sm"
            style={{
              backgroundColor: piece.color,
              left: `${piece.x}%`,
              top: `${piece.y}%`,
            }}
            initial={{
              y: -10,
              x: piece.x,
              rotate: piece.rotation,
              scale: piece.scale,
            }}
            animate={{
              y: 110,
              x: piece.x + (Math.random() - 0.5) * 20,
              rotate: piece.rotation + 360,
              scale: piece.scale,
            }}
            transition={{
              duration: duration / 1000,
              ease: 'easeOut',
            }}
            exit={{
              opacity: 0,
              scale: 0,
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
