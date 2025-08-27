"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { motion } from "framer-motion";
import {
    BarChart3,
    Clock,
    Download,
    Edit,
    FileText,
    PieChart,
    Play,
    Plus,
    Trash2,
    TrendingUp,
    Users
} from "lucide-react";
import { useEffect, useState } from "react";

interface CustomReport {
    id: string;
    name: string;
    description: string;
    report_type: string;
    is_scheduled: boolean;
    schedule_frequency: string;
    export_format: string;
    is_active: boolean;
    last_generated: string | null;
    created_at: string;
    updated_at: string;
}

interface ReportExecution {
    id: string;
    status: "running" | "completed" | "failed";
    started_at: string;
    completed_at: string | null;
    data_points: number | null;
    file_size_bytes: number | null;
    file_url: string | null;
    error_message: string | null;
}

export default function CustomReports() {
    const [reports, setReports] = useState<CustomReport[]>([]);
    const [executions, setExecutions] = useState<ReportExecution[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedReport, setSelectedReport] = useState<CustomReport | null>(null);
    const [formData, setFormData] = useState({
        name: "",
        description: "",
        report_type: "user_progress",
        is_scheduled: false,
        schedule_frequency: "weekly",
        export_format: "pdf",
        email_recipients: ""
    });

    useEffect(() => {
        fetchReports();
    }, []);

    const fetchReports = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/analytics/reports');
            const data = await response.json();
            setReports(data);
        } catch (error) {
            console.error('Error fetching reports:', error);
        } finally {
            setLoading(false);
        }
    };

    const createReport = async () => {
        try {
            const response = await fetch('/api/analytics/reports', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                setShowCreateForm(false);
                setFormData({
                    name: "",
                    description: "",
                    report_type: "user_progress",
                    is_scheduled: false,
                    schedule_frequency: "weekly",
                    export_format: "pdf",
                    email_recipients: ""
                });
                fetchReports();
            }
        } catch (error) {
            console.error('Error creating report:', error);
        }
    };

    const executeReport = async (reportId: string) => {
        try {
            const response = await fetch(`/api/analytics/reports/${reportId}/execute`, {
                method: 'POST',
            });

            if (response.ok) {
                const execution = await response.json();
                setExecutions(prev => [...prev, execution]);

                // Poll for completion
                pollExecutionStatus(execution.execution_id);
            }
        } catch (error) {
            console.error('Error executing report:', error);
        }
    };

    const pollExecutionStatus = async (executionId: string) => {
        const poll = async () => {
            try {
                const response = await fetch(`/api/analytics/executions/${executionId}`);
                const execution = await response.json();

                setExecutions(prev =>
                    prev.map(e => e.id === executionId ? execution : e)
                );

                if (execution.status === "running") {
                    setTimeout(poll, 2000);
                }
            } catch (error) {
                console.error('Error polling execution status:', error);
            }
        };

        poll();
    };

    const getReportTypeIcon = (type: string) => {
        switch (type) {
            case "user_progress":
                return <TrendingUp className="h-4 w-4" />;
            case "performance_analysis":
                return <BarChart3 className="h-4 w-4" />;
            case "engagement_metrics":
                return <Users className="h-4 w-4" />;
            case "content_effectiveness":
                return <PieChart className="h-4 w-4" />;
            default:
                return <FileText className="h-4 w-4" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "completed":
                return "bg-green-100 text-green-800";
            case "running":
                return "bg-blue-100 text-blue-800";
            case "failed":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
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
                    <h1 className="text-3xl font-bold tracking-tight">Custom Reports</h1>
                    <p className="text-muted-foreground">
                        Create and manage personalized analytics reports
                    </p>
                </div>
                <Button onClick={() => setShowCreateForm(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Report
                </Button>
            </div>

            {/* Create Report Form */}
            {showCreateForm && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                >
                    <Card>
                        <CardHeader>
                            <CardTitle>Create New Report</CardTitle>
                            <CardDescription>
                                Configure your custom analytics report
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="name">Report Name</Label>
                                    <Input
                                        id="name"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="Weekly Progress Report"
                                    />
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="report_type">Report Type</Label>
                                    <Select
                                        value={formData.report_type}
                                        onValueChange={(value) => setFormData({ ...formData, report_type: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="user_progress">User Progress</SelectItem>
                                            <SelectItem value="performance_analysis">Performance Analysis</SelectItem>
                                            <SelectItem value="engagement_metrics">Engagement Metrics</SelectItem>
                                            <SelectItem value="content_effectiveness">Content Effectiveness</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="export_format">Export Format</Label>
                                    <Select
                                        value={formData.export_format}
                                        onValueChange={(value) => setFormData({ ...formData, export_format: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="pdf">PDF</SelectItem>
                                            <SelectItem value="excel">Excel</SelectItem>
                                            <SelectItem value="csv">CSV</SelectItem>
                                            <SelectItem value="json">JSON</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="schedule_frequency">Schedule Frequency</Label>
                                    <Select
                                        value={formData.schedule_frequency}
                                        onValueChange={(value) => setFormData({ ...formData, schedule_frequency: value })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="daily">Daily</SelectItem>
                                            <SelectItem value="weekly">Weekly</SelectItem>
                                            <SelectItem value="monthly">Monthly</SelectItem>
                                            <SelectItem value="quarterly">Quarterly</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="description">Description</Label>
                                <Textarea
                                    id="description"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    placeholder="Describe what this report will contain..."
                                    rows={3}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="email_recipients">Email Recipients (optional)</Label>
                                <Input
                                    id="email_recipients"
                                    value={formData.email_recipients}
                                    onChange={(e) => setFormData({ ...formData, email_recipients: e.target.value })}
                                    placeholder="email1@example.com, email2@example.com"
                                />
                            </div>

                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="is_scheduled"
                                    checked={formData.is_scheduled}
                                    onCheckedChange={(checked) =>
                                        setFormData({ ...formData, is_scheduled: checked as boolean })
                                    }
                                />
                                <Label htmlFor="is_scheduled">Schedule this report</Label>
                            </div>

                            <div className="flex items-center space-x-2">
                                <Button onClick={createReport}>Create Report</Button>
                                <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                                    Cancel
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </motion.div>
            )}

            {/* Reports Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {reports.map((report, index) => (
                    <motion.div
                        key={report.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <Card className="h-full">
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        {getReportTypeIcon(report.report_type)}
                                        <CardTitle className="text-lg">{report.name}</CardTitle>
                                    </div>
                                    <Badge variant={report.is_active ? "default" : "secondary"}>
                                        {report.is_active ? "Active" : "Inactive"}
                                    </Badge>
                                </div>
                                <CardDescription>{report.description}</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-muted-foreground">Type:</span>
                                        <span className="capitalize">{report.report_type.replace('_', ' ')}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-muted-foreground">Format:</span>
                                        <span className="uppercase">{report.export_format}</span>
                                    </div>
                                    {report.is_scheduled && (
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">Schedule:</span>
                                            <span className="capitalize">{report.schedule_frequency}</span>
                                        </div>
                                    )}
                                    {report.last_generated && (
                                        <div className="flex items-center justify-between text-sm">
                                            <span className="text-muted-foreground">Last Generated:</span>
                                            <span>{new Date(report.last_generated).toLocaleDateString()}</span>
                                        </div>
                                    )}
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Button
                                        size="sm"
                                        onClick={() => executeReport(report.id)}
                                        className="flex-1"
                                    >
                                        <Play className="h-4 w-4 mr-2" />
                                        Execute
                                    </Button>
                                    <Button size="sm" variant="outline">
                                        <Edit className="h-4 w-4" />
                                    </Button>
                                    <Button size="sm" variant="outline">
                                        <Trash2 className="h-4 w-4" />
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>

            {/* Recent Executions */}
            {executions.length > 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Clock className="h-5 w-5" />
                            Recent Executions
                        </CardTitle>
                        <CardDescription>
                            Latest report execution status
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {executions.slice(0, 5).map((execution, index) => (
                                <motion.div
                                    key={execution.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: index * 0.1 }}
                                    className="flex items-center justify-between p-3 rounded-lg border"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-2 rounded-full ${execution.status === "completed" ? "bg-green-500" :
                                                execution.status === "running" ? "bg-blue-500" : "bg-red-500"
                                            }`}></div>
                                        <div>
                                            <p className="text-sm font-medium">
                                                Report Execution {execution.id.slice(0, 8)}
                                            </p>
                                            <p className="text-xs text-muted-foreground">
                                                Started: {new Date(execution.started_at).toLocaleString()}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Badge className={getStatusColor(execution.status)}>
                                            {execution.status}
                                        </Badge>
                                        {execution.status === "completed" && execution.file_url && (
                                            <Button size="sm" variant="outline">
                                                <Download className="h-4 w-4" />
                                            </Button>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Empty State */}
            {reports.length === 0 && !showCreateForm && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="text-center py-12"
                >
                    <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No Custom Reports</h3>
                    <p className="text-muted-foreground mb-4">
                        Create your first custom report to get started with personalized analytics.
                    </p>
                    <Button onClick={() => setShowCreateForm(true)}>
                        <Plus className="h-4 w-4 mr-2" />
                        Create Your First Report
                    </Button>
                </motion.div>
            )}
        </div>
    );
}
