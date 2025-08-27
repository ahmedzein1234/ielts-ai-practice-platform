"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { motion } from "framer-motion";
import {
    Activity,
    AlertTriangle,
    ArrowDownRight,
    ArrowUpRight,
    BarChart3,
    Brain,
    CheckCircle,
    Download,
    Eye,
    Lightbulb,
    Minus,
    RefreshCw,
    Target,
    TrendingUp
} from "lucide-react";
import { useEffect, useState } from "react";

interface AnalyticsSummary {
    total_events: number;
    total_metrics: number;
    total_predictions: number;
    total_reports: number;
    total_exports: number;
    recent_activity: Array<{
        type: string;
        timestamp: string;
        description: string;
        data: any;
    }>;
}

interface RealTimeMetric {
    metric_name: string;
    current_value: number;
    previous_value: number;
    change_percentage: number;
    trend: "increasing" | "decreasing" | "stable";
    last_updated: string;
}

interface TrendAnalysis {
    metric_name: string;
    trend_direction: "increasing" | "decreasing" | "stable";
    change_percentage: number;
    time_period: string;
    data_points: Array<{
        date: string;
        value: number;
        day: number;
    }>;
}

interface PredictiveInsight {
    insight_type: "improvement" | "decline" | "stable";
    title: string;
    description: string;
    confidence_score: number;
    predicted_value: number;
    target_date: string;
    factors: string[];
    recommendations: string[];
}

export default function AnalyticsDashboard() {
    const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary | null>(null);
    const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetric[]>([]);
    const [trends, setTrends] = useState<TrendAnalysis[]>([]);
    const [insights, setInsights] = useState<PredictiveInsight[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState("overview");

    useEffect(() => {
        fetchAnalyticsData();
    }, []);

    const fetchAnalyticsData = async () => {
        try {
            setLoading(true);

            // Fetch analytics summary
            const summaryResponse = await fetch('/api/analytics/summary');
            const summaryData = await summaryResponse.json();
            setAnalyticsSummary(summaryData);

            // Fetch real-time metrics
            const metricsResponse = await fetch('/api/analytics/realtime/metrics');
            const metricsData = await metricsResponse.json();
            setRealTimeMetrics(metricsData);

            // Fetch trend analysis for key metrics
            const trendPromises = ['reading_score', 'listening_score', 'writing_score', 'speaking_score'].map(
                metric => fetch(`/api/analytics/trends/${metric}?days=30`)
            );
            const trendResponses = await Promise.all(trendPromises);
            const trendData = await Promise.all(trendResponses.map(res => res.json()));
            setTrends(trendData);

            // Fetch predictive insights
            const insightsResponse = await fetch('/api/analytics/insights/predictive');
            const insightsData = await insightsResponse.json();
            setInsights(insightsData);

        } catch (error) {
            console.error('Error fetching analytics data:', error);
        } finally {
            setLoading(false);
        }
    };

    const getTrendIcon = (trend: string) => {
        switch (trend) {
            case "increasing":
                return <ArrowUpRight className="h-4 w-4 text-green-500" />;
            case "decreasing":
                return <ArrowDownRight className="h-4 w-4 text-red-500" />;
            default:
                return <Minus className="h-4 w-4 text-gray-500" />;
        }
    };

    const getTrendColor = (trend: string) => {
        switch (trend) {
            case "increasing":
                return "text-green-600";
            case "decreasing":
                return "text-red-600";
            default:
                return "text-gray-600";
        }
    };

    const getInsightIcon = (type: string) => {
        switch (type) {
            case "improvement":
                return <TrendingUp className="h-5 w-5 text-green-500" />;
            case "decline":
                return <AlertTriangle className="h-5 w-5 text-red-500" />;
            default:
                return <CheckCircle className="h-5 w-5 text-blue-500" />;
        }
    };

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
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
                    <p className="text-muted-foreground">
                        Comprehensive insights into your learning progress and performance
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button variant="outline" size="sm" onClick={fetchAnalyticsData}>
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                    </Button>
                </div>
            </div>

            {/* Quick Stats */}
            {analyticsSummary && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">Total Events</CardTitle>
                                <Activity className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{analyticsSummary.total_events.toLocaleString()}</div>
                                <p className="text-xs text-muted-foreground">
                                    +12% from last month
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
                                <CardTitle className="text-sm font-medium">Performance Metrics</CardTitle>
                                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{analyticsSummary.total_metrics.toLocaleString()}</div>
                                <p className="text-xs text-muted-foreground">
                                    +8% from last month
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
                                <CardTitle className="text-sm font-medium">Predictions</CardTitle>
                                <Brain className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{analyticsSummary.total_predictions}</div>
                                <p className="text-xs text-muted-foreground">
                                    +15% from last month
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
                                <CardTitle className="text-sm font-medium">Custom Reports</CardTitle>
                                <Eye className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{analyticsSummary.total_reports}</div>
                                <p className="text-xs text-muted-foreground">
                                    +5% from last month
                                </p>
                            </CardContent>
                        </Card>
                    </motion.div>
                </div>
            )}

            {/* Main Content Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="trends">Trends</TabsTrigger>
                    <TabsTrigger value="insights">AI Insights</TabsTrigger>
                    <TabsTrigger value="realtime">Real-time</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Recent Activity */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Activity className="h-5 w-5" />
                                    Recent Activity
                                </CardTitle>
                                <CardDescription>
                                    Your latest learning activities and interactions
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {analyticsSummary?.recent_activity.slice(0, 5).map((activity, index) => (
                                        <motion.div
                                            key={index}
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="flex items-center justify-between p-3 rounded-lg border"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                                <div>
                                                    <p className="text-sm font-medium">{activity.description}</p>
                                                    <p className="text-xs text-muted-foreground">
                                                        {new Date(activity.timestamp).toLocaleString()}
                                                    </p>
                                                </div>
                                            </div>
                                            <Badge variant="secondary" className="text-xs">
                                                {activity.type}
                                            </Badge>
                                        </motion.div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Performance Overview */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Target className="h-5 w-5" />
                                    Performance Overview
                                </CardTitle>
                                <CardDescription>
                                    Your current performance across all modules
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {['Reading', 'Listening', 'Writing', 'Speaking'].map((module, index) => (
                                        <motion.div
                                            key={module}
                                            initial={{ opacity: 0, x: 20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className="space-y-2"
                                        >
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium">{module}</span>
                                                <span className="text-sm text-muted-foreground">7.2</span>
                                            </div>
                                            <Progress value={72} className="h-2" />
                                        </motion.div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="trends" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {trends.map((trend, index) => (
                            <motion.div
                                key={trend.metric_name}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center justify-between">
                                            <span className="capitalize">{trend.metric_name.replace('_', ' ')}</span>
                                            <div className="flex items-center gap-2">
                                                {getTrendIcon(trend.trend_direction)}
                                                <span className={`text-sm font-medium ${getTrendColor(trend.trend_direction)}`}>
                                                    {trend.change_percentage > 0 ? '+' : ''}{trend.change_percentage.toFixed(1)}%
                                                </span>
                                            </div>
                                        </CardTitle>
                                        <CardDescription>
                                            {trend.time_period} trend analysis
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="h-32 flex items-end justify-between gap-1">
                                            {trend.data_points.slice(-7).map((point, i) => (
                                                <div
                                                    key={i}
                                                    className="flex-1 bg-primary/20 rounded-t"
                                                    style={{
                                                        height: `${(point.value / 9) * 100}%`,
                                                        minHeight: '4px'
                                                    }}
                                                />
                                            ))}
                                        </div>
                                        <div className="mt-4 text-center">
                                            <p className="text-sm text-muted-foreground">
                                                Trend: {trend.trend_direction}
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="insights" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {insights.map((insight, index) => (
                            <motion.div
                                key={insight.title}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            {getInsightIcon(insight.insight_type)}
                                            {insight.title}
                                        </CardTitle>
                                        <CardDescription>
                                            Confidence: {(insight.confidence_score * 100).toFixed(0)}%
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <p className="text-sm">{insight.description}</p>

                                        <div>
                                            <h4 className="text-sm font-medium mb-2">Key Factors:</h4>
                                            <ul className="text-sm text-muted-foreground space-y-1">
                                                {insight.factors.map((factor, i) => (
                                                    <li key={i} className="flex items-center gap-2">
                                                        <div className="w-1 h-1 bg-primary rounded-full"></div>
                                                        {factor}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>

                                        <div>
                                            <h4 className="text-sm font-medium mb-2">Recommendations:</h4>
                                            <ul className="text-sm text-muted-foreground space-y-1">
                                                {insight.recommendations.map((rec, i) => (
                                                    <li key={i} className="flex items-center gap-2">
                                                        <Lightbulb className="h-3 w-3 text-yellow-500" />
                                                        {rec}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>

                                        <div className="flex items-center justify-between pt-2 border-t">
                                            <span className="text-xs text-muted-foreground">
                                                Predicted: {insight.predicted_value.toFixed(1)}
                                            </span>
                                            <span className="text-xs text-muted-foreground">
                                                Target: {new Date(insight.target_date).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </TabsContent>

                <TabsContent value="realtime" className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {realTimeMetrics.map((metric, index) => (
                            <motion.div
                                key={metric.metric_name}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                            >
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center justify-between">
                                            <span className="capitalize">{metric.metric_name.replace('_', ' ')}</span>
                                            <div className="flex items-center gap-2">
                                                {getTrendIcon(metric.trend)}
                                                <span className={`text-sm font-medium ${getTrendColor(metric.trend)}`}>
                                                    {metric.change_percentage > 0 ? '+' : ''}{metric.change_percentage.toFixed(1)}%
                                                </span>
                                            </div>
                                        </CardTitle>
                                        <CardDescription>
                                            Last updated: {new Date(metric.last_updated).toLocaleTimeString()}
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-4">
                                            <div className="flex items-center justify-between">
                                                <span className="text-2xl font-bold">{metric.current_value}</span>
                                                <span className="text-sm text-muted-foreground">
                                                    Previous: {metric.previous_value}
                                                </span>
                                            </div>

                                            <div className="w-full bg-secondary rounded-full h-2">
                                                <div
                                                    className="bg-primary h-2 rounded-full transition-all duration-300"
                                                    style={{
                                                        width: `${Math.min(Math.max(metric.current_value / 9 * 100, 0), 100)}%`
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </motion.div>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
