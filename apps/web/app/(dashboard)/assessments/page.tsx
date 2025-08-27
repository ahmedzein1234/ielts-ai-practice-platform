"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { BookOpen, Clock, Play, Search, Target } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface MockTest {
    id: string;
    title: string;
    test_type: "academic" | "general";
    difficulty_level: "beginner" | "intermediate" | "advanced";
    duration_minutes: number;
    total_questions: number;
    is_active: boolean;
    created_at: string;
}

export default function AssessmentsPage() {
    const [tests, setTests] = useState<MockTest[]>([]);
    const [filteredTests, setFilteredTests] = useState<MockTest[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [testTypeFilter, setTestTypeFilter] = useState<string>("all");
    const [difficultyFilter, setDifficultyFilter] = useState<string>("all");
    const router = useRouter();

    useEffect(() => {
        fetchMockTests();
    }, []);

    useEffect(() => {
        filterTests();
    }, [tests, searchTerm, testTypeFilter, difficultyFilter]);

    const fetchMockTests = async () => {
        try {
            const response = await fetch("/api/assessments/tests");
            if (response.ok) {
                const data = await response.json();
                setTests(data);
            }
        } catch (error) {
            console.error("Error fetching mock tests:", error);
        } finally {
            setLoading(false);
        }
    };

    const filterTests = () => {
        let filtered = tests;

        // Filter by search term
        if (searchTerm) {
            filtered = filtered.filter(test =>
                test.title.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        // Filter by test type
        if (testTypeFilter !== "all") {
            filtered = filtered.filter(test => test.test_type === testTypeFilter);
        }

        // Filter by difficulty
        if (difficultyFilter !== "all") {
            filtered = filtered.filter(test => test.difficulty_level === difficultyFilter);
        }

        setFilteredTests(filtered);
    };

    const startTest = async (testId: string) => {
        try {
            const response = await fetch("/api/assessments/sessions", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ test_id: testId }),
            });

            if (response.ok) {
                const session = await response.json();
                router.push(`/assessments/test/${session.id}`);
            }
        } catch (error) {
            console.error("Error starting test:", error);
        }
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case "beginner":
                return "bg-green-100 text-green-800";
            case "intermediate":
                return "bg-yellow-100 text-yellow-800";
            case "advanced":
                return "bg-red-100 text-red-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
    };

    const getTestTypeColor = (type: string) => {
        switch (type) {
            case "academic":
                return "bg-blue-100 text-blue-800";
            case "general":
                return "bg-purple-100 text-purple-800";
            default:
                return "bg-gray-100 text-gray-800";
        }
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

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Mock Tests</h1>
                <p className="text-gray-600">
                    Practice with full-length IELTS mock tests to improve your skills and track your progress.
                </p>
            </div>

            {/* Filters */}
            <div className="mb-6 space-y-4">
                <div className="flex flex-col sm:flex-row gap-4">
                    <div className="flex-1">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                            <Input
                                placeholder="Search tests..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                    </div>
                    <Select value={testTypeFilter} onValueChange={setTestTypeFilter}>
                        <SelectTrigger className="w-full sm:w-48">
                            <SelectValue placeholder="Test Type" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Types</SelectItem>
                            <SelectItem value="academic">Academic</SelectItem>
                            <SelectItem value="general">General Training</SelectItem>
                        </SelectContent>
                    </Select>
                    <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
                        <SelectTrigger className="w-full sm:w-48">
                            <SelectValue placeholder="Difficulty" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Levels</SelectItem>
                            <SelectItem value="beginner">Beginner</SelectItem>
                            <SelectItem value="intermediate">Intermediate</SelectItem>
                            <SelectItem value="advanced">Advanced</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Test Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredTests.map((test) => (
                    <Card key={test.id} className="hover:shadow-lg transition-shadow">
                        <CardHeader>
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <CardTitle className="text-lg mb-2">{test.title}</CardTitle>
                                    <div className="flex gap-2 mb-3">
                                        <Badge className={getTestTypeColor(test.test_type)}>
                                            {test.test_type.charAt(0).toUpperCase() + test.test_type.slice(1)}
                                        </Badge>
                                        <Badge className={getDifficultyColor(test.difficulty_level)}>
                                            {test.difficulty_level.charAt(0).toUpperCase() + test.difficulty_level.slice(1)}
                                        </Badge>
                                    </div>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                <div className="flex items-center text-sm text-gray-600">
                                    <Clock className="h-4 w-4 mr-2" />
                                    {test.duration_minutes} minutes
                                </div>
                                <div className="flex items-center text-sm text-gray-600">
                                    <BookOpen className="h-4 w-4 mr-2" />
                                    {test.total_questions} questions
                                </div>
                                <div className="flex items-center text-sm text-gray-600">
                                    <Target className="h-4 w-4 mr-2" />
                                    All 4 modules
                                </div>
                            </div>

                            <Button
                                onClick={() => startTest(test.id)}
                                className="w-full mt-4"
                                disabled={!test.is_active}
                            >
                                <Play className="h-4 w-4 mr-2" />
                                {test.is_active ? "Start Test" : "Unavailable"}
                            </Button>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {filteredTests.length === 0 && (
                <div className="text-center py-12">
                    <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No tests found</h3>
                    <p className="text-gray-600">
                        Try adjusting your search criteria or check back later for new tests.
                    </p>
                </div>
            )}
        </div>
    );
}
