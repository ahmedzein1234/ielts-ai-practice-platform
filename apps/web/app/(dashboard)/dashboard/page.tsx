'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  Mic,
  PenTool,
  Headphones,
  BookOpen,
  TrendingUp,
  Target,
  Clock,
  Calendar,
  Award,
  ArrowRight,
  Play,
  Plus,
  BarChart3,
  Users,
  Trophy,
  Zap,
} from 'lucide-react';
import { useAuth } from '@/components/providers/auth-provider';

interface DashboardStats {
  totalSessions: number;
  averageScore: number;
  targetScore: number;
  daysUntilTest: number;
  streakDays: number;
  moduleScores: {
    speaking: number;
    writing: number;
    listening: number;
    reading: number;
  };
}

interface RecentActivity {
  id: string;
  type: 'speaking' | 'writing' | 'listening' | 'reading';
  title: string;
  score?: number;
  date: string;
  duration?: number;
}

const mockStats: DashboardStats = {
  totalSessions: 47,
  averageScore: 7.2,
  targetScore: 7.5,
  daysUntilTest: 14,
  streakDays: 8,
  moduleScores: {
    speaking: 7.0,
    writing: 6.5,
    listening: 7.5,
    reading: 7.8,
  },
};

const mockRecentActivity: RecentActivity[] = [
  {
    id: '1',
    type: 'speaking',
    title: 'Part 2: Describe a memorable journey',
    score: 7.2,
    date: '2024-01-15T10:30:00Z',
    duration: 15,
  },
  {
    id: '2',
    type: 'writing',
    title: 'Task 2: Technology and communication',
    score: 6.8,
    date: '2024-01-14T14:20:00Z',
  },
  {
    id: '3',
    type: 'listening',
    title: 'Academic Listening Test 3',
    score: 7.5,
    date: '2024-01-13T09:15:00Z',
    duration: 30,
  },
  {
    id: '4',
    type: 'reading',
    title: 'Academic Reading Passage 2',
    score: 7.8,
    date: '2024-01-12T16:45:00Z',
    duration: 60,
  },
];

const moduleConfig = {
  speaking: {
    icon: Mic,
    color: 'bg-blue-500',
    textColor: 'text-blue-600',
    bgColor: 'bg-blue-50',
    darkBgColor: 'dark:bg-blue-900/20',
  },
  writing: {
    icon: PenTool,
    color: 'bg-purple-500',
    textColor: 'text-purple-600',
    bgColor: 'bg-purple-50',
    darkBgColor: 'dark:bg-purple-900/20',
  },
  listening: {
    icon: Headphones,
    color: 'bg-green-500',
    textColor: 'text-green-600',
    bgColor: 'bg-green-50',
    darkBgColor: 'dark:bg-green-900/20',
  },
  reading: {
    icon: BookOpen,
    color: 'bg-orange-500',
    textColor: 'text-orange-600',
    bgColor: 'bg-orange-50',
    darkBgColor: 'dark:bg-orange-900/20',
  },
};

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>(mockStats);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>(mockRecentActivity);

  const getModuleIcon = (type: string) => {
    const config = moduleConfig[type as keyof typeof moduleConfig];
    return config?.icon || Mic;
  };

  const getModuleColor = (type: string) => {
    const config = moduleConfig[type as keyof typeof moduleConfig];
    return config?.color || 'bg-blue-500';
  };

  const getModuleTextColor = (type: string) => {
    const config = moduleConfig[type as keyof typeof moduleConfig];
    return config?.textColor || 'text-blue-600';
  };

  const getModuleBgColor = (type: string) => {
    const config = moduleConfig[type as keyof typeof moduleConfig];
    return `${config?.bgColor} ${config?.darkBgColor}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Yesterday';
    if (diffDays === 0) return 'Today';
    return `${diffDays} days ago`;
  };

  const getBandScoreClass = (score: number) => {
    if (score >= 7.5) return 'band-score-7-8';
    if (score >= 6.5) return 'band-score-5-6';
    if (score >= 5.5) return 'band-score-3-4';
    return 'band-score-1-2';
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome back, {user?.name?.split(' ')[0]}! 👋
        </h1>
        <p className="text-muted-foreground">
          Ready to continue your IELTS preparation journey? You have {stats.daysUntilTest} days until your test.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageScore}</div>
            <p className="text-xs text-muted-foreground">
              +0.3 from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Study Streak</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.streakDays} days</div>
            <p className="text-xs text-muted-foreground">
              Keep it up! 🔥
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Sessions</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalSessions}</div>
            <p className="text-xs text-muted-foreground">
              +5 this week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Days to Test</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.daysUntilTest}</div>
            <p className="text-xs text-muted-foreground">
              {stats.daysUntilTest <= 7 ? 'Final stretch!' : 'Keep practicing'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Module Progress */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Object.entries(stats.moduleScores).map(([module, score]) => {
          const Icon = getModuleIcon(module);
          const bgColor = getModuleBgColor(module);
          const textColor = getModuleTextColor(module);
          const progress = (score / 9) * 100;

          return (
            <Card key={module} className="relative overflow-hidden">
              <CardHeader className="pb-2">
                <div className="flex items-center space-x-2">
                  <div className={`p-2 rounded-lg ${bgColor}`}>
                    <Icon className={`h-4 w-4 ${textColor}`} />
                  </div>
                  <CardTitle className="text-sm font-medium capitalize">
                    {module}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <div className="text-2xl font-bold">{score}</div>
                  <Badge className={getBandScoreClass(score)}>
                    Band {Math.round(score)}
                  </Badge>
                </div>
                <Progress value={progress} className="h-2" />
                <p className="text-xs text-muted-foreground mt-2">
                  {progress.toFixed(0)}% of target
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Link href="/speaking">
          <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
            <CardHeader className="pb-2">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
                  <Mic className="h-4 w-4 text-blue-600" />
                </div>
                <CardTitle className="text-sm font-medium">Speaking</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Practice speaking</span>
                <Play className="h-4 w-4 text-muted-foreground group-hover:text-blue-600 transition-colors" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/writing">
          <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
            <CardHeader className="pb-2">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-purple-50 dark:bg-purple-900/20">
                  <PenTool className="h-4 w-4 text-purple-600" />
                </div>
                <CardTitle className="text-sm font-medium">Writing</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Write an essay</span>
                <Plus className="h-4 w-4 text-muted-foreground group-hover:text-purple-600 transition-colors" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/listening">
          <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
            <CardHeader className="pb-2">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/20">
                  <Headphones className="h-4 w-4 text-green-600" />
                </div>
                <CardTitle className="text-sm font-medium">Listening</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Take a test</span>
                <Play className="h-4 w-4 text-muted-foreground group-hover:text-green-600 transition-colors" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/reading">
          <Card className="hover:shadow-lg transition-all duration-200 cursor-pointer group">
            <CardHeader className="pb-2">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-orange-50 dark:bg-orange-900/20">
                  <BookOpen className="h-4 w-4 text-orange-600" />
                </div>
                <CardTitle className="text-sm font-medium">Reading</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Read passages</span>
                <Play className="h-4 w-4 text-muted-foreground group-hover:text-orange-600 transition-colors" />
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Recent Activity and Goals */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Your latest practice sessions and scores
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => {
                const Icon = getModuleIcon(activity.type);
                const bgColor = getModuleBgColor(activity.type);

                return (
                  <div key={activity.id} className="flex items-center space-x-4">
                    <div className={`p-2 rounded-lg ${bgColor}`}>
                      <Icon className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">
                        {activity.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(activity.date)}
                        {activity.duration && ` • ${activity.duration} min`}
                      </p>
                    </div>
                    {activity.score && (
                      <Badge className={getBandScoreClass(activity.score)}>
                        {activity.score}
                      </Badge>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="mt-4">
              <Link href="/analytics">
                <Button variant="outline" size="sm" className="w-full">
                  View all activity
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Goals and Achievements */}
        <Card>
          <CardHeader>
            <CardTitle>Goals & Achievements</CardTitle>
            <CardDescription>
              Track your progress towards your target score
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Target Score Progress */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Target Score</span>
                  <span className="text-sm text-muted-foreground">
                    {stats.averageScore} / {stats.targetScore}
                  </span>
                </div>
                <Progress 
                  value={(stats.averageScore / stats.targetScore) * 100} 
                  className="h-2" 
                />
                <p className="text-xs text-muted-foreground">
                  {((stats.averageScore / stats.targetScore) * 100).toFixed(0)}% of target reached
                </p>
              </div>

              {/* Study Streak */}
              <div className="flex items-center space-x-4 p-3 bg-gradient-to-r from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 rounded-lg">
                <div className="p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
                  <Award className="h-4 w-4 text-yellow-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Study Streak</p>
                  <p className="text-xs text-muted-foreground">
                    {stats.streakDays} days in a row! Keep it up!
                  </p>
                </div>
              </div>

              {/* Next Milestone */}
              <div className="flex items-center space-x-4 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg">
                <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <Target className="h-4 w-4 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Next Milestone</p>
                  <p className="text-xs text-muted-foreground">
                    Reach 7.5 average score (0.3 points away)
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-4">
              <Link href="/target">
                <Button variant="outline" size="sm" className="w-full">
                  Set new goals
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
