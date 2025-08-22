"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp,
  TrendingDown,
  Target,
  Calendar,
  Clock,
  Award,
  BarChart3,
  PieChart,
  Activity,
  Users,
  BookOpen,
  Mic,
  PenTool,
  Headphones
} from "lucide-react";

interface TestResult {
  id: string;
  module: "speaking" | "writing" | "listening" | "reading";
  score: number;
  date: string;
  duration: number;
  questions_answered: number;
  total_questions: number;
}

interface ProgressData {
  date: string;
  speaking: number;
  writing: number;
  listening: number;
  reading: number;
  overall: number;
}

const mockTestResults: TestResult[] = [
  { id: "1", module: "speaking", score: 7.5, date: "2024-01-15", duration: 15, questions_answered: 3, total_questions: 3 },
  { id: "2", module: "writing", score: 6.5, date: "2024-01-16", duration: 60, questions_answered: 2, total_questions: 2 },
  { id: "3", module: "listening", score: 8.0, date: "2024-01-17", duration: 30, questions_answered: 10, total_questions: 10 },
  { id: "4", module: "reading", score: 7.0, date: "2024-01-18", duration: 60, questions_answered: 13, total_questions: 13 },
  { id: "5", module: "speaking", score: 8.0, date: "2024-01-19", duration: 15, questions_answered: 3, total_questions: 3 },
  { id: "6", module: "writing", score: 7.0, date: "2024-01-20", duration: 60, questions_answered: 2, total_questions: 2 },
  { id: "7", module: "listening", score: 7.5, date: "2024-01-21", duration: 30, questions_answered: 10, total_questions: 10 },
  { id: "8", module: "reading", score: 6.5, date: "2024-01-22", duration: 60, questions_answered: 13, total_questions: 13 },
];

const mockProgressData: ProgressData[] = [
  { date: "2024-01-15", speaking: 7.5, writing: 0, listening: 0, reading: 0, overall: 7.5 },
  { date: "2024-01-16", speaking: 7.5, writing: 6.5, listening: 0, reading: 0, overall: 7.0 },
  { date: "2024-01-17", speaking: 7.5, writing: 6.5, listening: 8.0, reading: 0, overall: 7.3 },
  { date: "2024-01-18", speaking: 7.5, writing: 6.5, listening: 8.0, reading: 7.0, overall: 7.3 },
  { date: "2024-01-19", speaking: 8.0, writing: 6.5, listening: 8.0, reading: 7.0, overall: 7.4 },
  { date: "2024-01-20", speaking: 8.0, writing: 7.0, listening: 8.0, reading: 7.0, overall: 7.5 },
  { date: "2024-01-21", speaking: 8.0, writing: 7.0, listening: 7.5, reading: 7.0, overall: 7.4 },
  { date: "2024-01-22", speaking: 8.0, writing: 7.0, listening: 7.5, reading: 6.5, overall: 7.3 },
];

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState<"7d" | "30d" | "90d">("7d");
  const [testResults, setTestResults] = useState<TestResult[]>(mockTestResults);
  const [progressData, setProgressData] = useState<ProgressData[]>(mockProgressData);

  const getModuleIcon = (module: string) => {
    switch (module) {
      case "speaking": return <Mic className="w-4 h-4" />;
      case "writing": return <PenTool className="w-4 h-4" />;
      case "listening": return <Headphones className="w-4 h-4" />;
      case "reading": return <BookOpen className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getModuleColor = (module: string) => {
    switch (module) {
      case "speaking": return "text-blue-600";
      case "writing": return "text-purple-600";
      case "listening": return "text-green-600";
      case "reading": return "text-orange-600";
      default: return "text-gray-600";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 8.0) return "text-green-600";
    if (score >= 7.0) return "text-blue-600";
    if (score >= 6.0) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBadgeColor = (score: number) => {
    if (score >= 8.0) return "bg-green-100 text-green-800";
    if (score >= 7.0) return "bg-blue-100 text-blue-800";
    if (score >= 6.0) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  const calculateStats = () => {
    const totalTests = testResults.length;
    const averageScore = testResults.reduce((sum, test) => sum + test.score, 0) / totalTests;
    const totalTime = testResults.reduce((sum, test) => sum + test.duration, 0);
    const totalQuestions = testResults.reduce((sum, test) => sum + test.questions_answered, 0);

    const moduleScores = {
      speaking: testResults.filter(t => t.module === "speaking").reduce((sum, t) => sum + t.score, 0) / Math.max(1, testResults.filter(t => t.module === "speaking").length),
      writing: testResults.filter(t => t.module === "writing").reduce((sum, t) => sum + t.score, 0) / Math.max(1, testResults.filter(t => t.module === "writing").length),
      listening: testResults.filter(t => t.module === "listening").reduce((sum, t) => sum + t.score, 0) / Math.max(1, testResults.filter(t => t.module === "listening").length),
      reading: testResults.filter(t => t.module === "reading").reduce((sum, t) => sum + t.score, 0) / Math.max(1, testResults.filter(t => t.module === "reading").length),
    };

    return {
      totalTests,
      averageScore,
      totalTime,
      totalQuestions,
      moduleScores
    };
  };

  const stats = calculateStats();

  const recentTests = testResults.slice(-5).reverse();

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
        <p className="text-muted-foreground">Track your IELTS preparation progress and performance</p>
      </div>

      {/* Time Range Selector */}
      <div className="mb-6">
        <div className="flex gap-2">
          <Button
            variant={timeRange === "7d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("7d")}
          >
            Last 7 Days
          </Button>
          <Button
            variant={timeRange === "30d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("30d")}
          >
            Last 30 Days
          </Button>
          <Button
            variant={timeRange === "90d" ? "default" : "outline"}
            size="sm"
            onClick={() => setTimeRange("90d")}
          >
            Last 90 Days
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalTests}</div>
            <p className="text-xs text-muted-foreground">
              +2 from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Score</CardTitle>
            <Target className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${getScoreColor(stats.averageScore)}`}>
              {stats.averageScore.toFixed(1)}
            </div>
            <p className="text-xs text-muted-foreground">
              +0.3 from last week
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Study Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(stats.totalTime / 60)}h</div>
            <p className="text-xs text-muted-foreground">
              {stats.totalTime % 60}m total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Questions Answered</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalQuestions}</div>
            <p className="text-xs text-muted-foreground">
              +15 from last week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Module Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Module Performance
            </CardTitle>
            <CardDescription>Your average scores by module</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {Object.entries(stats.moduleScores).map(([module, score]) => (
              <div key={module} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-gray-100 ${getModuleColor(module)}`}>
                    {getModuleIcon(module)}
                  </div>
                  <div>
                    <p className="font-medium capitalize">{module}</p>
                    <p className="text-sm text-muted-foreground">
                      {testResults.filter(t => t.module === module).length} tests
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <Badge className={getScoreBadgeColor(score)}>
                    {score.toFixed(1)}
                  </Badge>
                  <div className="w-24 mt-2">
                    <Progress value={(score / 9) * 100} className="h-2" />
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Progress Trend
            </CardTitle>
            <CardDescription>Your overall score progression</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {progressData.map((data, index) => (
                <div key={index} className="flex flex-col items-center">
                  <div className="text-xs text-muted-foreground mb-1">
                    {new Date(data.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                  <div 
                    className="w-8 bg-blue-500 rounded-t"
                    style={{ height: `${(data.overall / 9) * 200}px` }}
                  ></div>
                  <div className="text-xs font-medium mt-1">
                    {data.overall.toFixed(1)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Tests */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Test Results</CardTitle>
          <CardDescription>Your latest practice test performances</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentTests.map((test) => (
              <div key={test.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`p-3 rounded-lg bg-gray-100 ${getModuleColor(test.module)}`}>
                    {getModuleIcon(test.module)}
                  </div>
                  <div>
                    <h3 className="font-medium capitalize">{test.module} Test</h3>
                    <p className="text-sm text-muted-foreground">
                      {new Date(test.date).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Score</p>
                    <Badge className={getScoreBadgeColor(test.score)}>
                      {test.score.toFixed(1)}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Duration</p>
                    <p className="font-medium">{test.duration}m</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Questions</p>
                    <p className="font-medium">{test.questions_answered}/{test.total_questions}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Achievements */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="w-5 h-5" />
              Achievements
            </CardTitle>
            <CardDescription>Milestones and accomplishments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-4 border rounded-lg">
                <div className="p-2 rounded-full bg-green-100">
                  <Target className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h4 className="font-medium">First Perfect Score</h4>
                  <p className="text-sm text-muted-foreground">Achieved 9.0 in Listening</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-4 border rounded-lg">
                <div className="p-2 rounded-full bg-blue-100">
                  <Clock className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium">Study Streak</h4>
                  <p className="text-sm text-muted-foreground">7 days in a row</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 p-4 border rounded-lg">
                <div className="p-2 rounded-full bg-purple-100">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium">Practice Master</h4>
                  <p className="text-sm text-muted-foreground">Completed 20+ tests</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Study Recommendations</CardTitle>
            <CardDescription>AI-powered suggestions to improve your performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Focus on Reading</h4>
                  <p className="text-sm text-blue-700">
                    Your reading score is 0.5 points below your target. Try practicing with more academic texts and focus on time management.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 bg-green-50 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-green-900">Great Progress in Speaking</h4>
                  <p className="text-sm text-green-700">
                    Your speaking score has improved by 0.5 points. Keep practicing with the conversation simulator.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 bg-yellow-50 rounded-lg">
                <TrendingDown className="w-5 h-5 text-yellow-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-yellow-900">Writing Needs Attention</h4>
                  <p className="text-sm text-yellow-700">
                    Consider reviewing grammar rules and essay structure. Your writing score has been consistent but could improve.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
