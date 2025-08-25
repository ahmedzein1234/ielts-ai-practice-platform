
import React from 'react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Target, Award } from 'lucide-react';

interface SkillProgress {
  skill: 'listening' | 'reading' | 'writing' | 'speaking';
  currentScore: number;
  targetScore: number;
  improvement: number;
}

interface ProgressChartProps {
  progress: SkillProgress[];
  overallScore: number;
  targetScore: number;
}

export function ProgressChart({ progress, overallScore, targetScore }: ProgressChartProps) {
  const getScoreColor = (score: number) => {
    if (score >= 7.0) return 'text-green-600';
    if (score >= 6.0) return 'text-yellow-600';
    if (score >= 5.0) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 8.0) return { variant: 'default', text: 'Expert' };
    if (score >= 7.0) return { variant: 'secondary', text: 'Advanced' };
    if (score >= 6.0) return { variant: 'outline', text: 'Intermediate' };
    return { variant: 'destructive', text: 'Beginner' };
  };

  const overallProgress = (overallScore / targetScore) * 100;
  const badge = getScoreBadge(overallScore);

  return (
    <Card className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Progress Overview</h3>
        <Badge variant={badge.variant as any}>
          <Award className="w-3 h-3 mr-1" />
          {badge.text}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Score</span>
            <span className={`text-lg font-bold ${getScoreColor(overallScore)}`}>
              {overallScore.toFixed(1)}
            </span>
          </div>
          <Progress value={overallProgress} className="h-2" />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Current: {overallScore.toFixed(1)}</span>
            <span>Target: {targetScore.toFixed(1)}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Improvement</span>
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +{progress.reduce((sum, p) => sum + p.improvement, 0).toFixed(1)}
              </span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            Average improvement across all skills
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Skill Breakdown</h4>
        {progress.map((skill) => (
          <div key={skill.skill} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium capitalize">
                  {skill.skill}
                </span>
                <Badge variant="outline" className="text-xs">
                  {skill.improvement > 0 ? '+' : ''}{skill.improvement.toFixed(1)}
                </Badge>
              </div>
              <span className={`text-sm font-bold ${getScoreColor(skill.currentScore)}`}>
                {skill.currentScore.toFixed(1)}
              </span>
            </div>
            <Progress 
              value={(skill.currentScore / skill.targetScore) * 100} 
              className="h-2" 
            />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Current: {skill.currentScore.toFixed(1)}</span>
              <span>Target: {skill.targetScore.toFixed(1)}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
