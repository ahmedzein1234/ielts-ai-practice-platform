"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
    BookOpen,
    Brain,
    CheckCircle,
    Clock,
    Eye,
    Lightbulb,
    PlayCircle,
    Sparkles,
    Target,
    Timer,
    TrendingUp,
    Zap
} from "lucide-react";
import { useEffect, useState } from "react";

interface Recommendation {
    id: string;
    title: string;
    description: string;
    reasoning: string;
    recommendation_type: string;
    confidence_score: number;
    priority_score: number;
    estimated_impact: number;
    time_to_complete: number;
    is_viewed: boolean;
    is_accepted: boolean;
    created_at: string;
    content_item_id?: string;
    learning_path_id?: string;
    action_type?: string;
    action_data?: any;
}

export default function RecommendationsPage() {
    const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("all");
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        fetchRecommendations();
    }, []);

    const fetchRecommendations = async () => {
        try {
            const response = await fetch("/api/learning/recommendations");
            if (response.ok) {
                const data = await response.json();
                setRecommendations(data);
            }
        } catch (error) {
            console.error("Failed to fetch recommendations:", error);
        } finally {
            setLoading(false);
        }
    };

    const generateRecommendations = async () => {
        setGenerating(true);
        try {
            const response = await fetch("/api/learning/recommendations/generate?limit=10", {
                method: "POST"
            });
            if (response.ok) {
                await fetchRecommendations(); // Refresh the list
            }
        } catch (error) {
            console.error("Failed to generate recommendations:", error);
        } finally {
            setGenerating(false);
        }
    };

    const markAsViewed = async (recommendationId: string) => {
        try {
            const response = await fetch(`/api/learning/recommendations/${recommendationId}/view`, {
                method: "PUT"
            });
            if (response.ok) {
                setRecommendations(prev =>
                    prev.map(rec =>
                        rec.id === recommendationId
                            ? { ...rec, is_viewed: true }
                            : rec
                    )
                );
            }
        } catch (error) {
            console.error("Failed to mark recommendation as viewed:", error);
        }
    };

    const acceptRecommendation = async (recommendationId: string) => {
        try {
            const response = await fetch(`/api/learning/recommendations/${recommendationId}/accept`, {
                method: "PUT"
            });
            if (response.ok) {
                setRecommendations(prev =>
                    prev.map(rec =>
                        rec.id === recommendationId
                            ? { ...rec, is_accepted: true }
                            : rec
                    )
                );
            }
        } catch (error) {
            console.error("Failed to accept recommendation:", error);
        }
    };

    const getRecommendationTypeIcon = (type: string) => {
        switch (type) {
            case "content_based":
                return <BookOpen className="w-4 h-4" />;
            case "performance_based":
                return <Target className="w-4 h-4" />;
            case "collaborative":
                return <Brain className="w-4 h-4" />;
            case "context_aware":
                return <Clock className="w-4 h-4" />;
            case "spaced_repetition":
                return <Timer className="w-4 h-4" />;
            default:
                return <Lightbulb className="w-4 h-4" />;
        }
    };

    const getRecommendationTypeColor = (type: string) => {
        switch (type) {
            case "content_based":
                return "bg-blue-100 text-blue-800";
            case "performance_based":
                return "bg-green-100 text-green-800";
            case "collaborative":
                return "bg-purple-100 text-purple-800";
            case "context_aware":
                return "bg-orange-100 text-orange-800";
            case "spaced_repetition":
                return "bg-pink-100 text-pink-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const getConfidenceColor = (score: number) => {
        if (score >= 0.8) return "text-green-600";
        if (score >= 0.6) return "text-yellow-600";
        return "text-red-600";
    };

    const getPriorityColor = (score: number) => {
        if (score >= 0.8) return "bg-red-100 text-red-800";
        if (score >= 0.6) return "bg-yellow-100 text-yellow-800";
        return "bg-green-100 text-green-800";
    };

    const filteredRecommendations = recommendations.filter(rec => {
        if (activeTab === "all") return true;
        if (activeTab === "pending") return !rec.is_viewed;
        if (activeTab === "accepted") return rec.is_accepted;
        if (activeTab === "viewed") return rec.is_viewed && !rec.is_accepted;
        return true;
    });

    const pendingCount = recommendations.filter(r => !r.is_viewed).length;
    const acceptedCount = recommendations.filter(r => r.is_accepted).length;
    const viewedCount = recommendations.filter(r => r.is_viewed && !r.is_accepted).length;

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
                    <h1 className="text-3xl font-bold tracking-tight">AI Recommendations</h1>
                    <p className="text-muted-foreground">
                        Personalized learning suggestions powered by AI
                    </p>
                </div>
                <Button onClick={generateRecommendations} disabled={generating}>
                    <Sparkles className="w-4 h-4 mr-2" />
                    {generating ? "Generating..." : "Generate New Recommendations"}
                </Button>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                            <CardTitle className="text-sm font-medium">Total Recommendations</CardTitle>
                            <Lightbulb className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{recommendations.length}</div>
                            <p className="text-xs text-muted-foreground">
                                AI-generated suggestions
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
                            <CardTitle className="text-sm font-medium">Pending</CardTitle>
                            <Eye className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{pendingCount}</div>
                            <p className="text-xs text-muted-foreground">
                                Awaiting your review
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
                            <CardTitle className="text-sm font-medium">Accepted</CardTitle>
                            <CheckCircle className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">{acceptedCount}</div>
                            <p className="text-xs text-muted-foreground">
                                Recommendations followed
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
                            <CardTitle className="text-sm font-medium">Average Impact</CardTitle>
                            <TrendingUp className="h-4 w-4 text-muted-foreground" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {recommendations.length > 0
                                    ? (recommendations.reduce((sum, r) => sum + (r.estimated_impact || 0), 0) / recommendations.length * 100).toFixed(1)
                                    : "0"
                                }%
                            </div>
                            <p className="text-xs text-muted-foreground">
                                Expected improvement
                            </p>
                        </CardContent>
                    </Card>
                </motion.div>
            </div>

            {/* Recommendations List */}
            <Card>
                <CardHeader>
                    <CardTitle>Your Recommendations</CardTitle>
                    <CardDescription>
                        AI-powered suggestions to optimize your learning journey
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="all">All ({recommendations.length})</TabsTrigger>
                            <TabsTrigger value="pending">Pending ({pendingCount})</TabsTrigger>
                            <TabsTrigger value="accepted">Accepted ({acceptedCount})</TabsTrigger>
                            <TabsTrigger value="viewed">Viewed ({viewedCount})</TabsTrigger>
                        </TabsList>

                        <TabsContent value={activeTab} className="space-y-4">
                            {filteredRecommendations.length === 0 ? (
                                <div className="text-center py-8">
                                    <Lightbulb className="mx-auto h-12 w-12 text-muted-foreground" />
                                    <h3 className="mt-2 text-sm font-semibold">No recommendations</h3>
                                    <p className="mt-1 text-sm text-muted-foreground">
                                        {activeTab === "all"
                                            ? "Generate your first AI recommendations to get started."
                                            : `No ${activeTab} recommendations found.`
                                        }
                                    </p>
                                    {activeTab === "all" && (
                                        <Button onClick={generateRecommendations} className="mt-4" disabled={generating}>
                                            <Sparkles className="w-4 h-4 mr-2" />
                                            {generating ? "Generating..." : "Generate Recommendations"}
                                        </Button>
                                    )}
                                </div>
                            ) : (
                                <div className="grid gap-4">
                                    {filteredRecommendations.map((recommendation, index) => (
                                        <motion.div
                                            key={recommendation.id}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                        >
                                            <Card className={`hover:shadow-md transition-shadow ${!recommendation.is_viewed ? 'border-l-4 border-l-blue-500' : ''
                                                }`}>
                                                <CardContent className="p-6">
                                                    <div className="flex items-start justify-between">
                                                        <div className="space-y-3 flex-1">
                                                            <div className="flex items-center gap-2">
                                                                <h3 className="text-lg font-semibold">{recommendation.title}</h3>
                                                                <Badge className={getRecommendationTypeColor(recommendation.recommendation_type)}>
                                                                    {getRecommendationTypeIcon(recommendation.recommendation_type)}
                                                                    <span className="ml-1 capitalize">
                                                                        {recommendation.recommendation_type.replace('_', ' ')}
                                                                    </span>
                                                                </Badge>
                                                                <Badge className={getPriorityColor(recommendation.priority_score)}>
                                                                    Priority: {(recommendation.priority_score * 100).toFixed(0)}%
                                                                </Badge>
                                                            </div>

                                                            <p className="text-sm text-muted-foreground">
                                                                {recommendation.description}
                                                            </p>

                                                            {recommendation.reasoning && (
                                                                <div className="bg-blue-50 p-3 rounded-lg">
                                                                    <p className="text-sm text-blue-800">
                                                                        <strong>Why this recommendation:</strong> {recommendation.reasoning}
                                                                    </p>
                                                                </div>
                                                            )}

                                                            <div className="flex items-center gap-6 text-sm">
                                                                <div className="flex items-center gap-1">
                                                                    <Zap className="w-4 h-4 text-muted-foreground" />
                                                                    <span>Impact: {(recommendation.estimated_impact * 100).toFixed(0)}%</span>
                                                                </div>
                                                                <div className="flex items-center gap-1">
                                                                    <Clock className="w-4 h-4 text-muted-foreground" />
                                                                    <span>{recommendation.time_to_complete} min</span>
                                                                </div>
                                                                <div className="flex items-center gap-1">
                                                                    <span className={`font-medium ${getConfidenceColor(recommendation.confidence_score)}`}>
                                                                        Confidence: {(recommendation.confidence_score * 100).toFixed(0)}%
                                                                    </span>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="flex flex-col gap-2 ml-4">
                                                            {!recommendation.is_viewed && (
                                                                <Button
                                                                    variant="outline"
                                                                    size="sm"
                                                                    onClick={() => markAsViewed(recommendation.id)}
                                                                >
                                                                    <Eye className="w-4 h-4 mr-1" />
                                                                    Mark Viewed
                                                                </Button>
                                                            )}
                                                            {!recommendation.is_accepted && (
                                                                <Button
                                                                    size="sm"
                                                                    onClick={() => acceptRecommendation(recommendation.id)}
                                                                >
                                                                    <CheckCircle className="w-4 h-4 mr-1" />
                                                                    Accept
                                                                </Button>
                                                            )}
                                                            {recommendation.is_accepted && (
                                                                <Badge className="bg-green-100 text-green-800">
                                                                    <CheckCircle className="w-4 h-4 mr-1" />
                                                                    Accepted
                                                                </Badge>
                                                            )}
                                                            <Button variant="ghost" size="sm">
                                                                <PlayCircle className="w-4 h-4 mr-1" />
                                                                Start
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

            {/* How It Works */}
            <Card>
                <CardHeader>
                    <CardTitle>How AI Recommendations Work</CardTitle>
                    <CardDescription>
                        Understanding how our AI creates personalized learning suggestions
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="text-center">
                            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Brain className="w-6 h-6 text-blue-600" />
                            </div>
                            <h3 className="font-semibold mb-2">Analyze Your Data</h3>
                            <p className="text-sm text-muted-foreground">
                                AI analyzes your test results, study patterns, and content preferences
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Target className="w-6 h-6 text-green-600" />
                            </div>
                            <h3 className="font-semibold mb-2">Identify Opportunities</h3>
                            <p className="text-sm text-muted-foreground">
                                Identifies skill gaps and learning opportunities based on your goals
                            </p>
                        </div>
                        <div className="text-center">
                            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Sparkles className="w-6 h-6 text-purple-600" />
                            </div>
                            <h3 className="font-semibold mb-2">Generate Suggestions</h3>
                            <p className="text-sm text-muted-foreground">
                                Creates personalized recommendations with confidence scores and impact estimates
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
