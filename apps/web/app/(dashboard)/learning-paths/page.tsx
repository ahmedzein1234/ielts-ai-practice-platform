"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
    Award,
    BarChart3,
    BookOpen,
    Calendar,
    CheckCircle,
    Clock,
    PlayCircle,
    Plus,
    Target,
    TrendingUp
} from "lucide-react";
import { useEffect, useState } from "react";

interface LearningPath {
    id: string;
    title: string;
    description: string;
    status: string;
    target_band_score: number;
    estimated_duration_days: number;
    completion_percentage: number;
    total_objectives: number;
    completed_objectives: number;
    created_at: string;
    started_at?: string;
    completed_at?: string;
}

interface LearningStats {
    total_learning_paths: number;
    active_learning_paths: number;
    completed_learning_paths: number;
    total_study_time_hours: number;
    average_daily_study_time: number;
    total_objectives_completed: number;
    current_streak_days: number;
    longest_streak_days: number;
    average_score: number;
    improvement_rate: number;
    skills_mastered: number;
    skills_in_progress: number;
    recommendations_accepted: number;
    recommendations_pending: number;
}

export default function LearningPathsPage() {
    const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
    const [stats, setStats] = useState<LearningStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("all");

    useEffect(() => {
        fetchLearningPaths();
        fetchLearningStats();
    }, []);

    const fetchLearningPaths = async () => {
        try {
            const response = await fetch("/api/learning/paths");
            if (response.ok) {
                const data = await response.json();
                setLearningPaths(data);
            }
        } catch (error) {
            console.error("Failed to fetch learning paths:", error);
        }
    };

    const fetchLearningStats = async () => {
        try {
            const response = await fetch("/api/learning/dashboard/stats");
            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error("Failed to fetch learning stats:", error);
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "active":
                return "bg-green-100 text-green-800";
            case "completed":
                return "bg-blue-100 text-blue-800";
            case "paused":
                return "bg-yellow-100 text-yellow-800";
            case "archived":
                return "bg-gray-100 text-gray-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case "active":
                return <PlayCircle className="w-4 h-4" />;
            case "completed":
                return <CheckCircle className="w-4 h-4" />;
            case "paused":
                return <Clock className="w-4 h-4" />;
            case "archived":
                return <BookOpen className="w-4 h-4" />;
            default:
                return <BookOpen className="w-4 h-4" />;
        }
    };

    const filteredPaths = learningPaths.filter(path => {
        if (activeTab === "all") return true;
        return path.status === activeTab;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Learning Paths</h1>
                    <p className="text-muted-foreground">
                        Your personalized learning journeys to IELTS success
                    </p>
                </div>
                <Button>
                    <Plus className="w-4 h-4 mr-2" />
                    Create New Path
                </Button>
            </div>

            {/* Stats Overview */}
            {stats && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Active Paths</CardTitle>
                                <BookOpen className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.active_learning_paths}</div>
                                <p className="text-xs text-muted-foreground">
                                    {stats.total_learning_paths} total paths
                                </p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                    >
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Study Time</CardTitle>
                                <Clock className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.total_study_time_hours.toFixed(1)}h</div>
                                <p className="text-xs text-muted-foreground">
                                    {stats.average_daily_study_time.toFixed(1)}h daily average
                                </p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Objectives Completed</CardTitle>
                                <CheckCircle className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.total_objectives_completed}</div>
                                <p className="text-xs text-muted-foreground">
                                    Current streak: {stats.current_streak_days} days
                                </p>
                            </CardContent>
                        </Card>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Average Score</CardTitle>
                                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats.average_score.toFixed(1)}</div>
                                <p className="text-xs text-muted-foreground">
                                    +{(stats.improvement_rate * 100).toFixed(1)}% improvement
                                </p>
                            </CardContent>
                        </Card>
                    </motion.div>
                </div>
            )}

            {/* Learning Paths */}
            <Card>
                <CardHeader>
                    <CardTitle>Your Learning Paths</CardTitle>
                    <CardDescription>
                        Track your progress through personalized learning journeys
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="all">All Paths</TabsTrigger>
                            <TabsTrigger value="active">Active</TabsTrigger>
                            <TabsTrigger value="completed">Completed</TabsTrigger>
                            <TabsTrigger value="paused">Paused</TabsTrigger>
                        </TabsList>

                        <TabsContent value={activeTab} className="space-y-4">
                            {filteredPaths.length === 0 ? (
                                <div className="text-center py-8">
                                    <BookOpen className="mx-auto h-12 w-12 text-muted-foreground" />
                                    <h3 className="mt-2 text-sm font-semibold">No learning paths</h3>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        {activeTab === "all"
                                            ? "Get started by creating your first learning path."
                                            : `No ${activeTab} learning paths found.`
                                        }
                                    </p>
                                    {activeTab === "all" && (
                                        <Button className="mt-4">
                                            <Plus className="w-4 h-4 mr-2" />
                                            Create Learning Path
                                        </Button>
                                    )}
                                </div>
                            ) : (
                                <div className="grid gap-4">
                                    {filteredPaths.map((path, index) => (
                                        <motion.div
                                            key={path.id}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <Card className="hover:shadow-md transition-shadow">
                                                <CardContent className="p-6">
                                                    <div className="flex items-start justify-between">
                                                        <div className="space-y-2 flex-1">
                                                            <div className="flex items-center gap-2">
                                                                <h3 className="text-lg font-semibold">{path.title}</h3>
                                                                <Badge className={getStatusColor(path.status)}>
                                                                    {getStatusIcon(path.status)}
                                                                    <span className="ml-1 capitalize">{path.status}</span>
                                                                </Badge>
                                                            </div>

                                                            <p className="text-sm text-muted-foreground">
                                                                {path.description}
                                                            </p>

                                                            <div className="flex items-center gap-6 text-sm">
                                                                <div className="flex items-center gap-1">
                                                                    <Target className="w-4 h-4 text-muted-foreground" />
                                                                    <span>Target: {path.target_band_score}</span>
                                                                </div>
                                                                <div className="flex items-center gap-1">
                                                                    <Calendar className="w-4 h-4 text-muted-foreground" />
                                                                    <span>{path.estimated_duration_days} days</span>
                                                                </div>
                                                                <div className="flex items-center gap-1">
                                                                    <CheckCircle className="w-4 h-4 text-muted-foreground" />
                                                                    <span>{path.completed_objectives}/{path.total_objectives} objectives</span>
                                                                </div>
                                                            </div>

                                                            <div className="space-y-2">
                                                                <div className="flex justify-between text-sm">
                                                                    <span>Progress</span>
                                                                    <span>{path.completion_percentage.toFixed(1)}%</span>
                                                                </div>
                                                                <Progress value={path.completion_percentage} className="h-2" />
                                                            </div>
                                                        </div>

                                                        <div className="flex flex-col gap-2 ml-4">
                                                            <Button variant="outline" size="sm">
                                                                <PlayCircle className="w-4 h-4 mr-1" />
                                                                Continue
                                                            </Button>
                                                            <Button variant="ghost" size="sm">
                                                                <BarChart3 className="w-4 h-4 mr-1" />
                                                                View Details
                                                            </Button>
                                                        </div>
                                                    </div>
                                                </CardContent>
                                            </Card>
                                        </motion.div>
                                    ))}
                                </div>
                            )}
                        </TabsContent>
                    </Tabs>
                </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Award className="w-5 h-5" />
                            Skill Mastery
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">
                            Track your progress across different skills
                        </p>
                        <Button variant="outline" className="w-full">
                            View Skills
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Recommendations
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">
                            Get personalized learning recommendations
                        </p>
                        <Button variant="outline" className="w-full">
                            View Recommendations
                        </Button>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart3 className="w-5 h-5" />
                            Analytics
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground mb-4">
                            Detailed insights into your learning progress
                        </p>
                        <Button variant="outline" className="w-full">
                            View Analytics
                        </Button>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
