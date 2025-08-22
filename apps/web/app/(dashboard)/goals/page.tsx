"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Target,
  Trophy,
  Award,
  TrendingUp,
  Calendar,
  Clock,
  Star,
  CheckCircle,
  XCircle,
  Plus,
  Edit,
  Trash2,
  BarChart3,
  Zap,
  Flame,
  Crown,
  Medal,
  Gift,
  Users,
  BookOpen
} from "lucide-react";

interface Goal {
  id: string;
  title: string;
  description: string;
  target_score: number;
  current_score: number;
  deadline: string;
  status: "active" | "completed" | "overdue";
  progress: number;
  created_date: string;
  modules: ("speaking" | "writing" | "listening" | "reading")[];
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: "score" | "streak" | "practice" | "social" | "special";
  unlocked: boolean;
  unlocked_date?: string;
  progress?: number;
  max_progress?: number;
  rarity: "common" | "rare" | "epic" | "legendary";
}

const mockGoals: Goal[] = [
  {
    id: "goal-1",
    title: "Achieve Band 7.5 Overall",
    description: "Target score for university admission requirements",
    target_score: 7.5,
    current_score: 7.2,
    deadline: "2024-03-15",
    status: "active",
    progress: 85,
    created_date: "2024-01-01",
    modules: ["speaking", "writing", "listening", "reading"]
  },
  {
    id: "goal-2",
    title: "Improve Speaking to 8.0",
    description: "Focus on speaking fluency and pronunciation",
    target_score: 8.0,
    current_score: 7.5,
    deadline: "2024-02-28",
    status: "active",
    progress: 75,
    created_date: "2024-01-10",
    modules: ["speaking"]
  },
  {
    id: "goal-3",
    title: "Complete 50 Practice Tests",
    description: "Build confidence through consistent practice",
    target_score: 50,
    current_score: 35,
    deadline: "2024-04-01",
    status: "active",
    progress: 70,
    created_date: "2024-01-05",
    modules: ["speaking", "writing", "listening", "reading"]
  }
];

const mockAchievements: Achievement[] = [
  {
    id: "ach-1",
    title: "First Steps",
    description: "Complete your first practice test",
    icon: "🎯",
    category: "practice",
    unlocked: true,
    unlocked_date: "2024-01-15",
    rarity: "common"
  },
  {
    id: "ach-2",
    title: "Band 7 Achiever",
    description: "Achieve a band score of 7.0 or higher",
    icon: "🏆",
    category: "score",
    unlocked: true,
    unlocked_date: "2024-01-20",
    rarity: "rare"
  },
  {
    id: "ach-3",
    title: "Study Streak",
    description: "Practice for 7 consecutive days",
    icon: "🔥",
    category: "streak",
    unlocked: true,
    unlocked_date: "2024-01-22",
    rarity: "common"
  },
  {
    id: "ach-4",
    title: "Perfect Score",
    description: "Achieve a perfect 9.0 in any module",
    icon: "👑",
    category: "score",
    unlocked: false,
    progress: 0,
    max_progress: 1,
    rarity: "legendary"
  },
  {
    id: "ach-5",
    title: "Social Butterfly",
    description: "Join 5 study groups and participate in discussions",
    icon: "🦋",
    category: "social",
    unlocked: false,
    progress: 2,
    max_progress: 5,
    rarity: "epic"
  },
  {
    id: "ach-6",
    title: "Practice Master",
    description: "Complete 100 practice tests",
    icon: "📚",
    category: "practice",
    unlocked: false,
    progress: 35,
    max_progress: 100,
    rarity: "epic"
  },
  {
    id: "ach-7",
    title: "Speed Demon",
    description: "Complete a full test in under 2 hours",
    icon: "⚡",
    category: "special",
    unlocked: false,
    rarity: "rare"
  },
  {
    id: "ach-8",
    title: "Grammar Guru",
    description: "Achieve 95% accuracy in grammar exercises",
    icon: "📝",
    category: "score",
    unlocked: false,
    progress: 78,
    max_progress: 95,
    rarity: "rare"
  }
];

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>(mockGoals);
  const [achievements, setAchievements] = useState<Achievement[]>(mockAchievements);
  const [showCreateGoal, setShowCreateGoal] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>("all");

  const unlockedAchievements = achievements.filter(a => a.unlocked);
  const lockedAchievements = achievements.filter(a => !a.unlocked);
  const totalAchievements = achievements.length;
  const unlockedCount = unlockedAchievements.length;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "active": return "bg-blue-100 text-blue-800";
      case "overdue": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case "common": return "bg-gray-100 text-gray-800";
      case "rare": return "bg-blue-100 text-blue-800";
      case "epic": return "bg-purple-100 text-purple-800";
      case "legendary": return "bg-yellow-100 text-yellow-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "score": return <Target className="w-4 h-4" />;
      case "streak": return <Flame className="w-4 h-4" />;
      case "practice": return <BookOpen className="w-4 h-4" />;
      case "social": return <Users className="w-4 h-4" />;
      case "special": return <Zap className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  };

  const filteredAchievements = filterCategory === "all" 
    ? achievements 
    : achievements.filter(a => a.category === filterCategory);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Goals & Achievements</h1>
        <p className="text-muted-foreground">Track your progress and celebrate your accomplishments</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Goals Section */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Your Goals</h2>
            <Button onClick={() => setShowCreateGoal(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Goal
            </Button>
          </div>

          <div className="space-y-4">
            {goals.map((goal) => (
              <Card key={goal.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="w-5 h-5" />
                        {goal.title}
                      </CardTitle>
                      <CardDescription>{goal.description}</CardDescription>
                    </div>
                    <Badge className={getStatusColor(goal.status)}>
                      {goal.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Progress</span>
                    <span className="text-sm font-medium">{goal.progress}%</span>
                  </div>
                  <Progress value={goal.progress} className="w-full" />
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Current Score</p>
                      <p className="font-semibold">{goal.current_score.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Target Score</p>
                      <p className="font-semibold">{goal.target_score.toFixed(1)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Deadline</p>
                      <p className="font-semibold">
                        {new Date(goal.deadline).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Days Left</p>
                      <p className="font-semibold">
                        {Math.max(0, Math.ceil((new Date(goal.deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24)))}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {goal.modules.map((module) => (
                      <Badge key={module} variant="outline" className="text-xs">
                        {module}
                      </Badge>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Edit className="w-4 h-4 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <BarChart3 className="w-4 h-4 mr-1" />
                      View Progress
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Achievements Section */}
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Achievements</h2>
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-yellow-500" />
              <span className="text-sm font-medium">
                {unlockedCount}/{totalAchievements}
              </span>
            </div>
          </div>

          {/* Achievement Stats */}
          <Card>
            <CardContent className="p-4">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-green-600">{unlockedCount}</div>
                  <div className="text-sm text-muted-foreground">Unlocked</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-600">
                    {achievements.filter(a => a.rarity === "rare" && a.unlocked).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Rare</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-purple-600">
                    {achievements.filter(a => a.rarity === "epic" && a.unlocked).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Epic</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Achievement Filters */}
          <div className="flex gap-2">
            <Button
              variant={filterCategory === "all" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterCategory("all")}
            >
              All
            </Button>
            <Button
              variant={filterCategory === "score" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterCategory("score")}
            >
              Score
            </Button>
            <Button
              variant={filterCategory === "streak" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterCategory("streak")}
            >
              Streak
            </Button>
            <Button
              variant={filterCategory === "practice" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterCategory("practice")}
            >
              Practice
            </Button>
            <Button
              variant={filterCategory === "social" ? "default" : "outline"}
              size="sm"
              onClick={() => setFilterCategory("social")}
            >
              Social
            </Button>
          </div>

          {/* Achievements Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredAchievements.map((achievement) => (
              <Card 
                key={achievement.id}
                className={`transition-all ${
                  achievement.unlocked 
                    ? 'border-green-200 bg-green-50' 
                    : 'border-gray-200 opacity-75'
                }`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`text-3xl ${achievement.unlocked ? '' : 'grayscale'}`}>
                      {achievement.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className={`font-semibold ${achievement.unlocked ? '' : 'text-gray-500'}`}>
                          {achievement.title}
                        </h3>
                        <Badge className={getRarityColor(achievement.rarity)}>
                          {achievement.rarity}
                        </Badge>
                      </div>
                      <p className={`text-sm ${achievement.unlocked ? 'text-gray-600' : 'text-gray-400'}`}>
                        {achievement.description}
                      </p>
                      
                      {achievement.unlocked && achievement.unlocked_date && (
                        <p className="text-xs text-green-600 mt-2">
                          Unlocked {new Date(achievement.unlocked_date).toLocaleDateString()}
                        </p>
                      )}
                      
                      {!achievement.unlocked && achievement.progress !== undefined && (
                        <div className="mt-2">
                          <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-500">Progress</span>
                            <span className="text-gray-500">
                              {achievement.progress}/{achievement.max_progress}
                            </span>
                          </div>
                          <Progress 
                            value={(achievement.progress / (achievement.max_progress || 1)) * 100} 
                            className="h-2"
                          />
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col items-center">
                      {achievement.unlocked ? (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      ) : (
                        <XCircle className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Achievements */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              Recent Achievements
            </CardTitle>
            <CardDescription>Your latest accomplishments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {unlockedAchievements.slice(0, 3).map((achievement) => (
                <div key={achievement.id} className="flex items-center gap-3 p-4 border rounded-lg">
                  <div className="text-2xl">{achievement.icon}</div>
                  <div>
                    <h4 className="font-medium">{achievement.title}</h4>
                    <p className="text-sm text-muted-foreground">
                      {achievement.unlocked_date && 
                        `Unlocked ${new Date(achievement.unlocked_date).toLocaleDateString()}`
                      }
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Achievement Leaderboard */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Crown className="w-5 h-5" />
              Achievement Leaderboard
            </CardTitle>
            <CardDescription>Top achievers this month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { name: "Sarah Johnson", achievements: 12, rank: 1 },
                { name: "Michael Chen", achievements: 10, rank: 2 },
                { name: "Emma Davis", achievements: 8, rank: 3 },
                { name: "Alex Thompson", achievements: 7, rank: 4 },
                { name: "Lisa Wang", achievements: 6, rank: 5 }
              ].map((user) => (
                <div key={user.rank} className="flex items-center gap-4 p-3 border rounded-lg">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold ${
                    user.rank === 1 ? 'bg-yellow-500' :
                    user.rank === 2 ? 'bg-gray-400' :
                    user.rank === 3 ? 'bg-orange-500' : 'bg-blue-500'
                  }`}>
                    {user.rank}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium">{user.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {user.achievements} achievements unlocked
                    </p>
                  </div>
                  <Trophy className="w-5 h-5 text-yellow-500" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
