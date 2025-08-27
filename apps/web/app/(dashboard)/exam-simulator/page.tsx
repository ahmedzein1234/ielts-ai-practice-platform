"use client";

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import {
    AlertCircle,
    CheckCircle,
    FileText, Headphones,
    Loader2,
    Mic,
    Pause,
    PenTool,
    Play,
    RotateCcw,
    SkipBack,
    SkipForward,
    Volume2, VolumeX
} from 'lucide-react';
import { useEffect, useState } from 'react';

interface ExamSection {
    id: string;
    title: string;
    skill: 'listening' | 'reading' | 'writing' | 'speaking';
    duration: number;
    instructions: string;
    questions: any[];
    completed: boolean;
    timeRemaining: number;
}

interface ExamSession {
    examId: string;
    examTitle: string;
    sections: ExamSection[];
    currentSection: number;
    isActive: boolean;
    startTime: Date | null;
    totalTimeRemaining: number;
}

export default function ExamSimulatorPage() {
    const [examSession, setExamSession] = useState<ExamSession | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isPaused, setIsPaused] = useState(false);
    const [showInstructions, setShowInstructions] = useState(true);
    const [audioEnabled, setAudioEnabled] = useState(true);
    const [currentQuestion, setCurrentQuestion] = useState(0);
    const [answers, setAnswers] = useState<Record<string, any>>({});

    // Timer effect
    useEffect(() => {
        if (!examSession?.isActive || isPaused) return;

        const timer = setInterval(() => {
            setExamSession(prev => {
                if (!prev) return prev;

                const newSections = [...prev.sections];
                const currentSection = newSections[prev.currentSection];

                if (currentSection.timeRemaining > 0) {
                    currentSection.timeRemaining -= 1;
                } else {
                    // Auto-advance to next section
                    if (prev.currentSection < newSections.length - 1) {
                        newSections[prev.currentSection + 1].timeRemaining = newSections[prev.currentSection + 1].duration * 60;
                        return {
                            ...prev,
                            sections: newSections,
                            currentSection: prev.currentSection + 1
                        };
                    } else {
                        // Exam completed
                        return {
                            ...prev,
                            isActive: false
                        };
                    }
                }

                return {
                    ...prev,
                    sections: newSections,
                    totalTimeRemaining: newSections.reduce((total, section) => total + section.timeRemaining, 0)
                };
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [examSession?.isActive, isPaused]);

    const startExam = async () => {
        setIsLoading(true);
        setError(null);

        try {
            // Simulate loading exam data
            await new Promise(resolve => setTimeout(resolve, 2000));

            const mockExamSession: ExamSession = {
                examId: 'mock_exam_001',
                examTitle: 'IELTS Academic Practice Test',
                sections: [
                    {
                        id: 'listening',
                        title: 'Listening',
                        skill: 'listening',
                        duration: 30,
                        instructions: 'You will hear 4 recordings. Answer 40 questions based on what you hear.',
                        questions: Array.from({ length: 40 }, (_, i) => ({
                            id: `listening_${i + 1}`,
                            number: i + 1,
                            type: 'multiple_choice',
                            text: `Question ${i + 1}: What is the main topic of the conversation?`,
                            options: ['A', 'B', 'C', 'D'],
                            audioTimestamp: i * 30
                        })),
                        completed: false,
                        timeRemaining: 30 * 60
                    },
                    {
                        id: 'reading',
                        title: 'Reading',
                        skill: 'reading',
                        duration: 60,
                        instructions: 'Read 3 passages and answer 40 questions.',
                        questions: Array.from({ length: 40 }, (_, i) => ({
                            id: `reading_${i + 1}`,
                            number: i + 1,
                            type: 'multiple_choice',
                            text: `Question ${i + 1}: According to the passage, what is the main argument?`,
                            options: ['A', 'B', 'C', 'D']
                        })),
                        completed: false,
                        timeRemaining: 60 * 60
                    },
                    {
                        id: 'writing',
                        title: 'Writing',
                        skill: 'writing',
                        duration: 60,
                        instructions: 'Complete 2 writing tasks within the time limit.',
                        questions: [
                            {
                                id: 'writing_task1',
                                number: 1,
                                type: 'essay',
                                text: 'Task 1: Describe the information shown in the chart below.',
                                timeLimit: 20,
                                wordLimit: 150
                            },
                            {
                                id: 'writing_task2',
                                number: 2,
                                type: 'essay',
                                text: 'Task 2: Discuss the advantages and disadvantages of remote work.',
                                timeLimit: 40,
                                wordLimit: 250
                            }
                        ],
                        completed: false,
                        timeRemaining: 60 * 60
                    },
                    {
                        id: 'speaking',
                        title: 'Speaking',
                        skill: 'speaking',
                        duration: 11,
                        instructions: 'Complete 3 speaking parts with the examiner.',
                        questions: [
                            {
                                id: 'speaking_part1',
                                number: 1,
                                type: 'conversation',
                                text: 'Part 1: Personal questions about your background and interests.',
                                timeLimit: 4
                            },
                            {
                                id: 'speaking_part2',
                                number: 2,
                                type: 'monologue',
                                text: 'Part 2: Speak for 2 minutes about a given topic.',
                                timeLimit: 3
                            },
                            {
                                id: 'speaking_part3',
                                number: 3,
                                type: 'discussion',
                                text: 'Part 3: Two-way discussion on abstract topics.',
                                timeLimit: 4
                            }
                        ],
                        completed: false,
                        timeRemaining: 11 * 60
                    }
                ],
                currentSection: 0,
                isActive: true,
                startTime: new Date(),
                totalTimeRemaining: 161 * 60 // 2h 41m
            };

            setExamSession(mockExamSession);
            setShowInstructions(false);
        } catch (error) {
            setError('Failed to start exam');
        } finally {
            setIsLoading(false);
        }
    };

    const pauseExam = () => {
        setIsPaused(true);
    };

    const resumeExam = () => {
        setIsPaused(false);
    };

    const completeSection = () => {
        if (!examSession) return;

        const newSections = [...examSession.sections];
        newSections[examSession.currentSection].completed = true;

        if (examSession.currentSection < newSections.length - 1) {
            // Move to next section
            setExamSession({
                ...examSession,
                sections: newSections,
                currentSection: examSession.currentSection + 1
            });
        } else {
            // Complete exam
            setExamSession({
                ...examSession,
                sections: newSections,
                isActive: false
            });
        }
    };

    const formatTime = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    };

    const getCurrentSection = () => {
        if (!examSession) return null;
        return examSession.sections[examSession.currentSection];
    };

    const getSectionIcon = (skill: string) => {
        switch (skill) {
            case 'listening': return <Headphones className="h-4 w-4" />;
            case 'reading': return <FileText className="h-4 w-4" />;
            case 'writing': return <PenTool className="h-4 w-4" />;
            case 'speaking': return <Mic className="h-4 w-4" />;
            default: return <FileText className="h-4 w-4" />;
        }
    };

    if (isLoading) {
        return (
            <div className="container mx-auto p-6">
                <div className="flex items-center justify-center min-h-[400px]">
                    <div className="text-center">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                        <p>Loading exam...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!examSession) {
        return (
            <div className="container mx-auto p-6">
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle>IELTS Exam Simulator</CardTitle>
                        <CardDescription>
                            Start a realistic IELTS exam simulation with timed sections
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="text-center p-4 border rounded-lg">
                                <Headphones className="h-8 w-8 mx-auto mb-2" />
                                <h3 className="font-semibold">Listening</h3>
                                <p className="text-sm text-muted-foreground">30 minutes</p>
                            </div>
                            <div className="text-center p-4 border rounded-lg">
                                <FileText className="h-8 w-8 mx-auto mb-2" />
                                <h3 className="font-semibold">Reading</h3>
                                <p className="text-sm text-muted-foreground">60 minutes</p>
                            </div>
                            <div className="text-center p-4 border rounded-lg">
                                <PenTool className="h-8 w-8 mx-auto mb-2" />
                                <h3 className="font-semibold">Writing</h3>
                                <p className="text-sm text-muted-foreground">60 minutes</p>
                            </div>
                            <div className="text-center p-4 border rounded-lg">
                                <Mic className="h-8 w-8 mx-auto mb-2" />
                                <h3 className="font-semibold">Speaking</h3>
                                <p className="text-sm text-muted-foreground">11 minutes</p>
                            </div>
                        </div>

                        <Button onClick={startExam} className="w-full" size="lg">
                            <Play className="mr-2 h-4 w-4" />
                            Start Exam Simulation
                        </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    const currentSection = getCurrentSection();

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Exam Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">{examSession.examTitle}</h1>
                    <p className="text-muted-foreground">
                        Section {examSession.currentSection + 1} of {examSession.sections.length}
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <div className="text-center">
                        <div className="text-lg font-bold text-red-600">
                            {formatTime(examSession.totalTimeRemaining)}
                        </div>
                        <div className="text-xs text-muted-foreground">Total Time</div>
                    </div>

                    <div className="flex gap-2">
                        {isPaused ? (
                            <Button onClick={resumeExam} variant="outline" size="sm">
                                <Play className="h-4 w-4" />
                            </Button>
                        ) : (
                            <Button onClick={pauseExam} variant="outline" size="sm">
                                <Pause className="h-4 w-4" />
                            </Button>
                        )}

                        <Button variant="outline" size="sm" onClick={() => setAudioEnabled(!audioEnabled)}>
                            {audioEnabled ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Section Progress */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {examSession.sections.map((section, index) => (
                    <Card
                        key={section.id}
                        className={`cursor-pointer transition-colors ${index === examSession.currentSection ? 'ring-2 ring-blue-500' : ''
                            } ${section.completed ? 'bg-green-50' : ''}`}
                        onClick={() => {
                            if (section.completed || index <= examSession.currentSection) {
                                setExamSession({
                                    ...examSession,
                                    currentSection: index
                                });
                            }
                        }}
                    >
                        <CardContent className="p-4">
                            <div className="flex items-center gap-2 mb-2">
                                {getSectionIcon(section.skill)}
                                <span className="font-semibold capitalize">{section.skill}</span>
                                {section.completed && <CheckCircle className="h-4 w-4 text-green-600" />}
                            </div>
                            <div className="text-sm text-muted-foreground">
                                {formatTime(section.timeRemaining)}
                            </div>
                            <Progress
                                value={((section.duration * 60 - section.timeRemaining) / (section.duration * 60)) * 100}
                                className="mt-2"
                            />
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Current Section */}
            {currentSection && (
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    {getSectionIcon(currentSection.skill)}
                                    {currentSection.title}
                                </CardTitle>
                                <CardDescription>
                                    {currentSection.instructions}
                                </CardDescription>
                            </div>
                            <div className="text-right">
                                <div className="text-lg font-bold text-red-600">
                                    {formatTime(currentSection.timeRemaining)}
                                </div>
                                <div className="text-xs text-muted-foreground">Time Remaining</div>
                            </div>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <Tabs defaultValue="questions" className="space-y-4">
                            <TabsList>
                                <TabsTrigger value="questions">Questions</TabsTrigger>
                                <TabsTrigger value="instructions">Instructions</TabsTrigger>
                                <TabsTrigger value="progress">Progress</TabsTrigger>
                            </TabsList>

                            <TabsContent value="questions" className="space-y-4">
                                {currentSection.skill === 'listening' && (
                                    <div className="space-y-4">
                                        <div className="bg-gray-100 p-4 rounded-lg">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Volume2 className="h-4 w-4" />
                                                <span className="font-semibold">Audio Player</span>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Button size="sm" variant="outline">
                                                    <SkipBack className="h-3 w-3" />
                                                </Button>
                                                <Button size="sm">
                                                    <Play className="h-3 w-3" />
                                                </Button>
                                                <Button size="sm" variant="outline">
                                                    <SkipForward className="h-3 w-3" />
                                                </Button>
                                                <div className="flex-1 bg-white rounded h-2">
                                                    <div className="bg-blue-500 h-2 rounded" style={{ width: '30%' }}></div>
                                                </div>
                                                <span className="text-sm">1:23 / 4:15</span>
                                            </div>
                                        </div>

                                        <div className="space-y-4">
                                            {currentSection.questions.slice(0, 5).map((question) => (
                                                <div key={question.id} className="border rounded-lg p-4">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="font-semibold">Question {question.number}</span>
                                                        <Badge variant="outline">{question.type}</Badge>
                                                    </div>
                                                    <p className="mb-3">{question.text}</p>
                                                    <div className="space-y-2">
                                                        {question.options?.map((option: string) => (
                                                            <label key={option} className="flex items-center space-x-2 cursor-pointer">
                                                                <input type="radio" name={question.id} value={option} />
                                                                <span>{option}</span>
                                                            </label>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {currentSection.skill === 'reading' && (
                                    <div className="space-y-4">
                                        <div className="bg-gray-50 p-4 rounded-lg">
                                            <h3 className="font-semibold mb-2">Reading Passage 1</h3>
                                            <p className="text-sm text-muted-foreground">
                                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                                            </p>
                                        </div>

                                        <div className="space-y-4">
                                            {currentSection.questions.slice(0, 5).map((question) => (
                                                <div key={question.id} className="border rounded-lg p-4">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="font-semibold">Question {question.number}</span>
                                                        <Badge variant="outline">{question.type}</Badge>
                                                    </div>
                                                    <p className="mb-3">{question.text}</p>
                                                    <div className="space-y-2">
                                                        {question.options?.map((option: string) => (
                                                            <label key={option} className="flex items-center space-x-2 cursor-pointer">
                                                                <input type="radio" name={question.id} value={option} />
                                                                <span>{option}</span>
                                                            </label>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {currentSection.skill === 'writing' && (
                                    <div className="space-y-4">
                                        {currentSection.questions.map((task) => (
                                            <div key={task.id} className="border rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h3 className="font-semibold">Task {task.number}</h3>
                                                    <Badge variant="outline">{task.timeLimit} minutes</Badge>
                                                </div>
                                                <p className="mb-3">{task.text}</p>
                                                <Textarea
                                                    placeholder={`Write your answer here (minimum ${task.wordLimit} words)...`}
                                                    className="min-h-[200px]"
                                                />
                                                <div className="flex items-center justify-between mt-2">
                                                    <span className="text-sm text-muted-foreground">
                                                        Word count: 0 / {task.wordLimit}
                                                    </span>
                                                    <span className="text-sm text-muted-foreground">
                                                        Time remaining: {task.timeLimit}:00
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {currentSection.skill === 'speaking' && (
                                    <div className="space-y-4">
                                        <div className="bg-blue-50 p-4 rounded-lg">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Mic className="h-4 w-4" />
                                                <span className="font-semibold">Speaking Test</span>
                                            </div>
                                            <p className="text-sm text-muted-foreground">
                                                You will be speaking with an AI examiner. Make sure your microphone is working properly.
                                            </p>
                                        </div>

                                        {currentSection.questions.map((part) => (
                                            <div key={part.id} className="border rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-3">
                                                    <h3 className="font-semibold">Part {part.number}</h3>
                                                    <Badge variant="outline">{part.timeLimit} minutes</Badge>
                                                </div>
                                                <p className="mb-3">{part.text}</p>
                                                <div className="flex gap-2">
                                                    <Button>
                                                        <Mic className="mr-2 h-4 w-4" />
                                                        Start Recording
                                                    </Button>
                                                    <Button variant="outline">
                                                        <RotateCcw className="mr-2 h-4 w-4" />
                                                        Practice Mode
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </TabsContent>

                            <TabsContent value="instructions">
                                <div className="space-y-4">
                                    <h3 className="font-semibold">Section Instructions</h3>
                                    <p>{currentSection.instructions}</p>

                                    <div className="bg-yellow-50 p-4 rounded-lg">
                                        <h4 className="font-semibold mb-2">Important Notes:</h4>
                                        <ul className="text-sm space-y-1">
                                            <li>• You cannot go back to previous sections once completed</li>
                                            <li>• Time will automatically advance to the next section</li>
                                            <li>• Make sure to save your answers before time runs out</li>
                                            <li>• You can pause the exam if needed</li>
                                        </ul>
                                    </div>
                                </div>
                            </TabsContent>

                            <TabsContent value="progress">
                                <div className="space-y-4">
                                    <h3 className="font-semibold">Section Progress</h3>
                                    <div className="space-y-2">
                                        {currentSection.questions.map((question, index) => (
                                            <div key={question.id} className="flex items-center justify-between p-2 border rounded">
                                                <span>Question {question.number}</span>
                                                <Badge variant={index < 3 ? "default" : "secondary"}>
                                                    {index < 3 ? "Answered" : "Not answered"}
                                                </Badge>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-blue-600">
                                            {Math.round((3 / currentSection.questions.length) * 100)}%
                                        </div>
                                        <div className="text-sm text-muted-foreground">Complete</div>
                                    </div>
                                </div>
                            </TabsContent>
                        </Tabs>

                        <div className="flex justify-between mt-6">
                            <Button
                                variant="outline"
                                disabled={examSession.currentSection === 0}
                                onClick={() => {
                                    if (examSession.currentSection > 0) {
                                        setExamSession({
                                            ...examSession,
                                            currentSection: examSession.currentSection - 1
                                        });
                                    }
                                }}
                            >
                                Previous Section
                            </Button>

                            <Button
                                onClick={completeSection}
                                disabled={currentSection.timeRemaining > 0}
                            >
                                {examSession.currentSection < examSession.sections.length - 1
                                    ? "Next Section"
                                    : "Complete Exam"
                                }
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            )}

            {error && (
                <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            {/* Pause Alert */}
            {isPaused && (
                <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                        Your exam is currently paused. The timer will resume when you continue.
                        <div className="flex gap-2 mt-2">
                            <Button onClick={resumeExam} size="sm">
                                Resume Exam
                            </Button>
                            <Button variant="outline" size="sm">
                                Exit Exam
                            </Button>
                        </div>
                    </AlertDescription>
                </Alert>
            )}
        </div>
    );
}
