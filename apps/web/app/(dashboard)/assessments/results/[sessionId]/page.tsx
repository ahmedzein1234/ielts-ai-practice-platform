"use client";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
    ArrowLeft,
    BookOpen,
    CheckCircle,
    Clock,
    Download,
    Share2,
    Star,
    Target,
    TrendingUp,
    Trophy,
    XCircle
} from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface TestResult {
    session_id: string;
    overall_score: number;
    module_scores: {
        listening: number;
        reading: number;
        writing: number;
        speaking: number;
    };
    total_questions: number;
    correct_answers: number;
    time_taken: number;
    band_score: number;
    detailed_feedback: {
        overall_performance: string;
        module_analysis: Record<string, string>;
        recommendations: string[];
    };
}

export default function TestResultsPage() {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.sessionId as string;

    const [result, setResult] = useState<TestResult | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (sessionId) {
            fetchTestResult();
        }
    }, [sessionId]);

    const fetchTestResult = async () => {
        try {
            const response = await fetch(`/api/assessments/sessions/${sessionId}/complete`, {
                method: "POST",
            });

            if (response.ok) {
                const data = await response.json();
                setResult(data);
            }
        } catch (error) {
            console.error("Error fetching test result:", error);
        } finally {
            setLoading(false);
        }
    };

    const getBandScoreColor = (bandScore: number) => {
        if (bandScore >= 7.0) return "text-green-600";
        if (bandScore >= 6.0) return "text-blue-600";
        if (bandScore >= 5.0) return "text-yellow-600";
        return "text-red-600";
    };

    const getPerformanceColor = (score: number) => {
        if (score >= 80) return "text-green-600";
        if (score >= 70) return "text-blue-600";
        if (score >= 60) return "text-yellow-600";
        return "text-red-600";
    };

    const getModuleIcon = (module: string) => {
        switch (module) {
            case "listening":
                return "🎧";
            case "reading":
                return "📖";
            case "writing":
                return "✍️";
            case "speaking":
                return "🗣️";
            default:
                return "📝";
        }
    };

    const formatTime = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
    };

    if (loading) {
        return (
            <div className="container mx-auto px-4 py-8">
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            </div>
        );
    }

    if (!result) {
        return (
            <div className="container mx-auto px-4 py-8">
                <Alert>
                    <XCircle className="h-4 w-4" />
                    <AlertDescription>
                        Test result not found. Please try again.
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    const accuracy = (result.correct_answers / result.total_questions) * 100;

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <Button
                            variant="outline"
                            onClick={() => router.push("/assessments")}
                            className="mb-4"
                        >
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Tests
                        </Button>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Test Results</h1>
                        <p className="text-gray-600">
                            Your IELTS mock test performance analysis
                        </p>
                    </div>
                    <div className="flex space-x-2">
                        <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-2" />
                            Download Report
                        </Button>
                        <Button variant="outline" size="sm">
                            <Share2 className="h-4 w-4 mr-2" />
                            Share Results
                        </Button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Results */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Overall Score Card */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Trophy className="h-6 w-6 text-yellow-500" />
                                <span>Overall Performance</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="text-center">
                                    <div className={`text-4xl font-bold ${getBandScoreColor(result.band_score)}`}>
                                        {result.band_score.toFixed(1)}
                                    </div>
                                    <div className="text-sm text-gray-600 mt-1">Band Score</div>
                                    <div className="flex justify-center mt-2">
                                        {[...Array(9)].map((_, i) => (
                                            <Star
                                                key={i}
                                                className={`h-4 w-4 ${i < Math.floor(result.band_score)
                                                    ? "text-yellow-400 fill-current"
                                                    : "text-gray-300"
                                                    }`}
                                            />
                                        ))}
                                    </div>
                                </div>

                                <div className="text-center">
                                    <div className={`text-4xl font-bold ${getPerformanceColor(result.overall_score)}`}>
                                        {result.overall_score.toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-gray-600 mt-1">Overall Score</div>
                                    <Progress value={result.overall_score} className="mt-2" />
                                </div>

                                <div className="text-center">
                                    <div className="text-4xl font-bold text-blue-600">
                                        {accuracy.toFixed(1)}%
                                    </div>
                                    <div className="text-sm text-gray-600 mt-1">Accuracy</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {result.correct_answers}/{result.total_questions} correct
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Module Scores */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <Target className="h-6 w-6 text-blue-500" />
                                <span>Module Performance</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {Object.entries(result.module_scores).map(([module, score]) => (
                                    <div key={module} className="flex items-center space-x-4">
                                        <div className="flex items-center space-x-3 flex-1">
                                            <span className="text-2xl">{getModuleIcon(module)}</span>
                                            <div className="flex-1">
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="font-medium capitalize">{module}</span>
                                                    <span className={`font-bold ${getPerformanceColor(score)}`}>
                                                        {score.toFixed(1)}%
                                                    </span>
                                                </div>
                                                <Progress value={score} className="h-2" />
                                            </div>
                                        </div>
                                        <Badge variant={score >= 70 ? "default" : "secondary"}>
                                            {result.detailed_feedback.module_analysis[module]}
                                        </Badge>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Recommendations */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center space-x-2">
                                <TrendingUp className="h-6 w-6 text-green-500" />
                                <span>Recommendations</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {result.detailed_feedback.recommendations.map((recommendation, index) => (
                                    <div key={index} className="flex items-start space-x-3">
                                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                                        <p className="text-gray-700">{recommendation}</p>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Test Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Test Summary</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Duration</span>
                                <div className="flex items-center space-x-2">
                                    <Clock className="h-4 w-4 text-gray-400" />
                                    <span className="font-medium">{formatTime(result.time_taken)}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Questions</span>
                                <div className="flex items-center space-x-2">
                                    <BookOpen className="h-4 w-4 text-gray-400" />
                                    <span className="font-medium">{result.total_questions}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Correct Answers</span>
                                <div className="flex items-center space-x-2">
                                    <CheckCircle className="h-4 w-4 text-green-500" />
                                    <span className="font-medium">{result.correct_answers}</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between">
                                <span className="text-gray-600">Performance</span>
                                <Badge variant={result.overall_score >= 70 ? "default" : "secondary"}>
                                    {result.detailed_feedback.overall_performance}
                                </Badge>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Quick Actions */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3">
                            <Button className="w-full" onClick={() => router.push("/assessments")}>
                                Take Another Test
                            </Button>
                            <Button variant="outline" className="w-full" onClick={() => router.push("/analytics")}>
                                View Analytics
                            </Button>
                            <Button variant="outline" className="w-full" onClick={() => router.push("/ai-tutor")}>
                                Get AI Tutor Help
                            </Button>
                        </CardContent>
                    </Card>

                    {/* Performance Insights */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Performance Insights</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3 text-sm">
                                <div className="p-3 bg-blue-50 rounded-lg">
                                    <div className="font-medium text-blue-900">Strong Areas</div>
                                    <div className="text-blue-700 mt-1">
                                        {Object.entries(result.module_scores)
                                            .filter(([_, score]) => score >= 70)
                                            .map(([module, _]) => module.charAt(0).toUpperCase() + module.slice(1))
                                            .join(", ") || "Keep practicing to identify your strengths"}
                                    </div>
                                </div>

                                <div className="p-3 bg-yellow-50 rounded-lg">
                                    <div className="font-medium text-yellow-900">Areas for Improvement</div>
                                    <div className="text-yellow-700 mt-1">
                                        {Object.entries(result.module_scores)
                                            .filter(([_, score]) => score < 70)
                                            .map(([module, _]) => module.charAt(0).toUpperCase() + module.slice(1))
                                            .join(", ") || "Great job! All areas are performing well"}
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
