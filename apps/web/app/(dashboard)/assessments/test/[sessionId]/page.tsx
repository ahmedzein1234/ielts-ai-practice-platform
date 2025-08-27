"use client";

import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, ArrowLeft, ArrowRight, CheckCircle, Clock, Flag } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface TestQuestion {
    id: string;
    module_type: "listening" | "reading" | "writing" | "speaking";
    question_number: number;
    question_data: {
        question_text: string;
        options?: string[];
        question_type: string;
        module_specific_data: any;
    };
    points: number;
}

interface TestSession {
    id: string;
    status: "started" | "in_progress" | "completed" | "abandoned";
    start_time: string;
    end_time?: string;
}

export default function TestInterface() {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.sessionId as string;

    const [session, setSession] = useState<TestSession | null>(null);
    const [questions, setQuestions] = useState<TestQuestion[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<string, any>>({});
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [showConfirmSubmit, setShowConfirmSubmit] = useState(false);

    useEffect(() => {
        if (sessionId) {
            fetchSessionData();
        }
    }, [sessionId]);

    useEffect(() => {
        if (timeRemaining > 0) {
            const timer = setInterval(() => {
                setTimeRemaining(prev => {
                    if (prev <= 1) {
                        handleTimeUp();
                        return 0;
                    }
                    return prev - 1;
                });
            }, 1000);

            return () => clearInterval(timer);
        }
    }, [timeRemaining]);

    const fetchSessionData = async () => {
        try {
            // Fetch session details
            const sessionResponse = await fetch(`/api/assessments/sessions/${sessionId}`);
            if (sessionResponse.ok) {
                const sessionData = await sessionResponse.json();
                setSession(sessionData);

                // Calculate time remaining (assuming 2h 45m = 165 minutes)
                const startTime = new Date(sessionData.start_time);
                const now = new Date();
                const elapsedMinutes = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60));
                const remainingMinutes = Math.max(0, 165 - elapsedMinutes);
                setTimeRemaining(remainingMinutes * 60); // Convert to seconds
            }

            // Fetch questions
            const questionsResponse = await fetch(`/api/assessments/sessions/${sessionId}/questions`);
            if (questionsResponse.ok) {
                const questionsData = await questionsResponse.json();
                setQuestions(questionsData);
            }
        } catch (error) {
            console.error("Error fetching session data:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswerChange = (questionId: string, answer: any) => {
        setAnswers(prev => ({
            ...prev,
            [questionId]: answer
        }));
    };

    const handleTimeUp = async () => {
        await submitTest();
    };

    const submitTest = async () => {
        setSubmitting(true);
        try {
            // Submit all answers
            for (const [questionId, answer] of Object.entries(answers)) {
                await fetch(`/api/assessments/sessions/${sessionId}/answers`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        question_id: questionId,
                        user_answer: answer,
                        time_spent: 0 // You could track actual time spent per question
                    }),
                });
            }

            // Complete the test
            const completeResponse = await fetch(`/api/assessments/sessions/${sessionId}/complete`, {
                method: "POST",
            });

            if (completeResponse.ok) {
                const result = await completeResponse.json();
                router.push(`/assessments/results/${sessionId}`);
            }
        } catch (error) {
            console.error("Error submitting test:", error);
        } finally {
            setSubmitting(false);
        }
    };

    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    const getModuleColor = (moduleType: string) => {
        switch (moduleType) {
            case "listening":
                return "bg-blue-100 text-blue-800";
            case "reading":
                return "bg-green-100 text-green-800";
            case "writing":
                return "bg-purple-100 text-purple-800";
            case "speaking":
                return "bg-orange-100 text-orange-800";
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

    if (!session || !questions.length) {
        return (
            <div className="container mx-auto px-4 py-8">
                <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Test session not found or no questions available.
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <div className="bg-white border-b sticky top-0 z-10">
                <div className="container mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => router.push("/assessments")}
                            >
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Back to Tests
                            </Button>
                            <div>
                                <h1 className="text-lg font-semibold">IELTS Mock Test</h1>
                                <p className="text-sm text-gray-600">
                                    Question {currentQuestionIndex + 1} of {questions.length}
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2 bg-red-50 px-3 py-2 rounded-lg">
                                <Clock className="h-4 w-4 text-red-600" />
                                <span className="font-mono text-red-600">
                                    {formatTime(timeRemaining)}
                                </span>
                            </div>

                            <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => setShowConfirmSubmit(true)}
                                disabled={submitting}
                            >
                                Submit Test
                            </Button>
                        </div>
                    </div>

                    <div className="mt-4">
                        <Progress value={progress} className="h-2" />
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Question Panel */}
                    <div className="lg:col-span-3">
                        <Card>
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <Badge className={getModuleColor(currentQuestion.module_type)}>
                                            {currentQuestion.module_type.charAt(0).toUpperCase() + currentQuestion.module_type.slice(1)}
                                        </Badge>
                                        <span className="text-sm text-gray-600">
                                            Question {currentQuestion.question_number}
                                        </span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <Flag className="h-4 w-4 text-gray-400" />
                                        <span className="text-sm text-gray-600">
                                            {currentQuestion.points} point{currentQuestion.points !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                </div>
                            </CardHeader>

                            <CardContent>
                                <div className="space-y-6">
                                    {/* Question Text */}
                                    <div>
                                        <h3 className="text-lg font-medium mb-4">
                                            {currentQuestion.question_data.question_text}
                                        </h3>
                                    </div>

                                    {/* Answer Options */}
                                    {currentQuestion.question_data.options && (
                                        <div className="space-y-3">
                                            {currentQuestion.question_data.options.map((option, index) => (
                                                <label
                                                    key={index}
                                                    className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                                                >
                                                    <input
                                                        type="radio"
                                                        name={`question-${currentQuestion.id}`}
                                                        value={option}
                                                        checked={answers[currentQuestion.id] === option}
                                                        onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                                                        className="h-4 w-4 text-primary"
                                                    />
                                                    <span>{option}</span>
                                                </label>
                                            ))}
                                        </div>
                                    )}

                                    {/* Text Input for other question types */}
                                    {!currentQuestion.question_data.options && (
                                        <div>
                                            <textarea
                                                placeholder="Enter your answer..."
                                                value={answers[currentQuestion.id] || ""}
                                                onChange={(e) => handleAnswerChange(currentQuestion.id, e.target.value)}
                                                className="w-full p-3 border rounded-lg resize-none"
                                                rows={4}
                                            />
                                        </div>
                                    )}
                                </div>
                            </CardContent>
                        </Card>

                        {/* Navigation */}
                        <div className="flex items-center justify-between mt-6">
                            <Button
                                variant="outline"
                                onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
                                disabled={currentQuestionIndex === 0}
                            >
                                <ArrowLeft className="h-4 w-4 mr-2" />
                                Previous
                            </Button>

                            <div className="flex items-center space-x-2">
                                {answers[currentQuestion.id] && (
                                    <CheckCircle className="h-4 w-4 text-green-600" />
                                )}
                                <span className="text-sm text-gray-600">
                                    {answers[currentQuestion.id] ? "Answered" : "Not answered"}
                                </span>
                            </div>

                            <Button
                                onClick={() => setCurrentQuestionIndex(prev => Math.min(questions.length - 1, prev + 1))}
                                disabled={currentQuestionIndex === questions.length - 1}
                            >
                                Next
                                <ArrowRight className="h-4 w-4 ml-2" />
                            </Button>
                        </div>
                    </div>

                    {/* Question Navigator */}
                    <div className="lg:col-span-1">
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Question Navigator</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="grid grid-cols-5 gap-2">
                                    {questions.map((question, index) => (
                                        <button
                                            key={question.id}
                                            onClick={() => setCurrentQuestionIndex(index)}
                                            className={`
                        p-2 text-sm rounded border transition-colors
                        ${index === currentQuestionIndex
                                                    ? 'bg-primary text-primary-foreground border-primary'
                                                    : answers[question.id]
                                                        ? 'bg-green-100 text-green-800 border-green-200'
                                                        : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200'
                                                }
                      `}
                                        >
                                            {index + 1}
                                        </button>
                                    ))}
                                </div>

                                <div className="mt-4 space-y-2 text-sm">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 bg-primary rounded"></div>
                                        <span>Current</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 bg-green-100 border border-green-200 rounded"></div>
                                        <span>Answered</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-4 h-4 bg-gray-100 border border-gray-200 rounded"></div>
                                        <span>Unanswered</span>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>

            {/* Confirm Submit Modal */}
            {showConfirmSubmit && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <Card className="w-full max-w-md mx-4">
                        <CardHeader>
                            <CardTitle>Confirm Test Submission</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-gray-600 mb-4">
                                Are you sure you want to submit your test? This action cannot be undone.
                            </p>
                            <div className="flex space-x-3">
                                <Button
                                    variant="outline"
                                    onClick={() => setShowConfirmSubmit(false)}
                                    className="flex-1"
                                >
                                    Cancel
                                </Button>
                                <Button
                                    onClick={submitTest}
                                    disabled={submitting}
                                    className="flex-1"
                                >
                                    {submitting ? "Submitting..." : "Submit Test"}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
