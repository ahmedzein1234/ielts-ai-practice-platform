"use client";

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Clock, Download, FileText, Headphones, Loader2, Mic, PenTool, Play, Settings, Target } from 'lucide-react';
import { useEffect, useState } from 'react';

interface ExamTemplate {
    exam_type: 'academic' | 'general';
    difficulty_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
    skill_types: string[];
    exam_structure: any;
    topics: any;
}

interface GeneratedExam {
    exam_id: string;
    exam: any;
    content: any;
    message: string;
}

export default function ExamCreatorPage() {
    const [examTemplate, setExamTemplate] = useState<ExamTemplate | null>(null);
    const [selectedExamType, setSelectedExamType] = useState<'academic' | 'general'>('academic');
    const [selectedDifficulty, setSelectedDifficulty] = useState<'beginner' | 'intermediate' | 'advanced' | 'expert'>('intermediate');
    const [customTopics, setCustomTopics] = useState<string[]>([]);
    const [includeAudio, setIncludeAudio] = useState(true);
    const [includeSpeaking, setIncludeSpeaking] = useState(true);
    const [examDuration, setExamDuration] = useState<number | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedExam, setGeneratedExam] = useState<GeneratedExam | null>(null);
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);

    // Load exam templates on component mount
    useEffect(() => {
        loadExamTemplates();
    }, []);

    const loadExamTemplates = async () => {
        try {
            const response = await fetch('http://localhost:8006/exam-templates');
            if (response.ok) {
                const data = await response.json();
                setExamTemplate(data);
            }
        } catch (error) {
            console.error('Failed to load exam templates:', error);
            setError('Failed to load exam templates');
        }
    };

    const generateExam = async () => {
        setIsGenerating(true);
        setProgress(0);
        setError(null);

        try {
            // Simulate progress updates
            const progressInterval = setInterval(() => {
                setProgress(prev => Math.min(prev + 10, 90));
            }, 1000);

            const requestBody = {
                exam_type: selectedExamType,
                difficulty_level: selectedDifficulty,
                custom_topics: customTopics.length > 0 ? customTopics : undefined,
                include_audio: includeAudio,
                include_speaking: includeSpeaking,
                exam_duration: examDuration
            };

            const response = await fetch('http://localhost:8006/generate-exam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody),
            });

            clearInterval(progressInterval);

            if (response.ok) {
                const examData = await response.json();
                setGeneratedExam(examData);
                setProgress(100);
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to generate exam');
            }
        } catch (error) {
            console.error('Error generating exam:', error);
            setError(error instanceof Error ? error.message : 'Failed to generate exam');
        } finally {
            setIsGenerating(false);
        }
    };

    const addCustomTopic = () => {
        const topic = prompt('Enter a custom topic:');
        if (topic && !customTopics.includes(topic)) {
            setCustomTopics([...customTopics, topic]);
        }
    };

    const removeCustomTopic = (topic: string) => {
        setCustomTopics(customTopics.filter(t => t !== topic));
    };

    const getDifficultyDescription = (difficulty: string) => {
        const descriptions = {
            beginner: 'Band 4-5: Basic understanding and communication',
            intermediate: 'Band 5-6: Competent user with some inaccuracies',
            advanced: 'Band 6-7: Good user with occasional inaccuracies',
            expert: 'Band 7-9: Very good to expert user'
        };
        return descriptions[difficulty as keyof typeof descriptions];
    };

    const getExamDuration = () => {
        if (examDuration) return examDuration;

        const baseDuration = selectedExamType === 'academic' ? 161 : 161; // 2h 41m
        return includeSpeaking ? baseDuration : baseDuration - 11;
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">IELTS Exam Creator</h1>
                    <p className="text-muted-foreground">
                        Generate comprehensive IELTS practice tests with AI-powered content
                    </p>
                </div>
                <Badge variant="secondary" className="text-sm">
                    Powered by OpenRouter AI
                </Badge>
            </div>

            <Tabs defaultValue="create" className="space-y-6">
                <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="create">Create Exam</TabsTrigger>
                    <TabsTrigger value="templates">Exam Templates</TabsTrigger>
                    <TabsTrigger value="results">Generated Exams</TabsTrigger>
                </TabsList>

                <TabsContent value="create" className="space-y-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Exam Configuration */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Settings className="h-5 w-5" />
                                    Exam Configuration
                                </CardTitle>
                                <CardDescription>
                                    Configure your IELTS exam parameters
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <Label htmlFor="exam-type">Exam Type</Label>
                                    <Select value={selectedExamType} onValueChange={(value: 'academic' | 'general') => setSelectedExamType(value)}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="academic">Academic IELTS</SelectItem>
                                            <SelectItem value="general">General Training IELTS</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="difficulty">Difficulty Level</Label>
                                    <Select value={selectedDifficulty} onValueChange={(value: 'beginner' | 'intermediate' | 'advanced' | 'expert') => setSelectedDifficulty(value)}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="beginner">Beginner (Band 4-5)</SelectItem>
                                            <SelectItem value="intermediate">Intermediate (Band 5-6)</SelectItem>
                                            <SelectItem value="advanced">Advanced (Band 6-7)</SelectItem>
                                            <SelectItem value="expert">Expert (Band 7-9)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                    <p className="text-sm text-muted-foreground">
                                        {getDifficultyDescription(selectedDifficulty)}
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label>Custom Topics (Optional)</Label>
                                    <div className="flex flex-wrap gap-2">
                                        {customTopics.map((topic, index) => (
                                            <Badge key={index} variant="secondary" className="cursor-pointer" onClick={() => removeCustomTopic(topic)}>
                                                {topic} ×
                                            </Badge>
                                        ))}
                                    </div>
                                    <Button variant="outline" size="sm" onClick={addCustomTopic}>
                                        Add Topic
                                    </Button>
                                </div>

                                <div className="space-y-2">
                                    <Label>Features</Label>
                                    <div className="space-y-2">
                                        <div className="flex items-center space-x-2">
                                            <Checkbox
                                                id="include-audio"
                                                checked={includeAudio}
                                                onCheckedChange={(checked) => setIncludeAudio(checked as boolean)}
                                            />
                                            <Label htmlFor="include-audio">Include Audio for Listening</Label>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <Checkbox
                                                id="include-speaking"
                                                checked={includeSpeaking}
                                                onCheckedChange={(checked) => setIncludeSpeaking(checked as boolean)}
                                            />
                                            <Label htmlFor="include-speaking">Include Speaking Section</Label>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="duration">Custom Duration (minutes)</Label>
                                    <Input
                                        id="duration"
                                        type="number"
                                        placeholder="Leave empty for standard duration"
                                        value={examDuration || ''}
                                        onChange={(e) => setExamDuration(e.target.value ? parseInt(e.target.value) : null)}
                                    />
                                </div>
                            </CardContent>
                        </Card>

                        {/* Exam Preview */}
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2">
                                    <Target className="h-5 w-5" />
                                    Exam Preview
                                </CardTitle>
                                <CardDescription>
                                    Preview of your exam configuration
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="space-y-2">
                                    <h4 className="font-semibold">Exam Structure</h4>
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <Headphones className="h-4 w-4" />
                                            <span>Listening: 30 minutes</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <FileText className="h-4 w-4" />
                                            <span>Reading: 60 minutes</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <PenTool className="h-4 w-4" />
                                            <span>Writing: 60 minutes</span>
                                        </div>
                                        {includeSpeaking && (
                                            <div className="flex items-center gap-2">
                                                <Mic className="h-4 w-4" />
                                                <span>Speaking: 11 minutes</span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <h4 className="font-semibold">Total Duration</h4>
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-4 w-4" />
                                        <span>{getExamDuration()} minutes</span>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <h4 className="font-semibold">Target Band Score</h4>
                                    <div className="flex items-center gap-2">
                                        <Target className="h-4 w-4" />
                                        <span>
                                            {selectedDifficulty === 'beginner' && '4.0 - 5.0'}
                                            {selectedDifficulty === 'intermediate' && '5.0 - 6.0'}
                                            {selectedDifficulty === 'advanced' && '6.0 - 7.0'}
                                            {selectedDifficulty === 'expert' && '7.0 - 9.0'}
                                        </span>
                                    </div>
                                </div>

                                <Button
                                    onClick={generateExam}
                                    disabled={isGenerating}
                                    className="w-full"
                                >
                                    {isGenerating ? (
                                        <>
                                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            Generating Exam...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="mr-2 h-4 w-4" />
                                            Generate Exam
                                        </>
                                    )}
                                </Button>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Progress and Results */}
                    {isGenerating && (
                        <Card>
                            <CardHeader>
                                <CardTitle>Generating Exam</CardTitle>
                                <CardDescription>
                                    Creating comprehensive IELTS exam content...
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <Progress value={progress} className="w-full" />
                                <p className="text-sm text-muted-foreground mt-2">
                                    {progress < 30 && "Initializing exam structure..."}
                                    {progress >= 30 && progress < 60 && "Generating listening content..."}
                                    {progress >= 60 && progress < 80 && "Creating reading passages..."}
                                    {progress >= 80 && progress < 100 && "Finalizing writing and speaking tasks..."}
                                    {progress === 100 && "Exam generated successfully!"}
                                </p>
                            </CardContent>
                        </Card>
                    )}

                    {error && (
                        <Alert variant="destructive">
                            <AlertDescription>{error}</AlertDescription>
                        </Alert>
                    )}

                    {generatedExam && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="flex items-center justify-between">
                                    <span>Generated Exam: {generatedExam.exam.title}</span>
                                    <Badge variant="default">{generatedExam.exam_id}</Badge>
                                </CardTitle>
                                <CardDescription>
                                    {generatedExam.exam.description}
                                </CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-blue-600">4</div>
                                        <div className="text-sm text-muted-foreground">Sections</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-green-600">{getExamDuration()}</div>
                                        <div className="text-sm text-muted-foreground">Minutes</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-purple-600">40</div>
                                        <div className="text-sm text-muted-foreground">Questions</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-2xl font-bold text-orange-600">{selectedDifficulty}</div>
                                        <div className="text-sm text-muted-foreground">Level</div>
                                    </div>
                                </div>

                                <div className="flex gap-2">
                                    <Button variant="outline" className="flex-1">
                                        <Download className="mr-2 h-4 w-4" />
                                        Download PDF
                                    </Button>
                                    <Button variant="outline" className="flex-1">
                                        <Play className="mr-2 h-4 w-4" />
                                        Start Exam
                                    </Button>
                                    <Button variant="outline" className="flex-1">
                                        <Settings className="mr-2 h-4 w-4" />
                                        Edit Exam
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                </TabsContent>

                <TabsContent value="templates" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>IELTS Exam Templates</CardTitle>
                            <CardDescription>
                                Standard exam structures and configurations
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {examTemplate ? (
                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-lg font-semibold mb-3">Exam Types</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {examTemplate.exam_type ? [examTemplate.exam_type] : ['general', 'academic'].map((type: string) => (
                                                <Card key={type} className="p-4">
                                                    <h4 className="font-semibold capitalize">{type} IELTS</h4>
                                                    <p className="text-sm text-muted-foreground">
                                                        {type === 'academic'
                                                            ? 'For university admission and professional registration'
                                                            : 'For work, training, or migration purposes'
                                                        }
                                                    </p>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-lg font-semibold mb-3">Difficulty Levels</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                            {examTemplate.difficulty_level ? [examTemplate.difficulty_level] : ['beginner', 'intermediate', 'advanced', 'expert'].map((level: string) => (
                                                <Card key={level} className="p-4">
                                                    <h4 className="font-semibold capitalize">{level}</h4>
                                                    <p className="text-sm text-muted-foreground">
                                                        {getDifficultyDescription(level)}
                                                    </p>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-lg font-semibold mb-3">Skill Types</h3>
                                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                            {examTemplate.skill_types.map((skill: string) => (
                                                <Card key={skill} className="p-4">
                                                    <h4 className="font-semibold capitalize">{skill}</h4>
                                                    <div className="flex items-center gap-2 mt-2">
                                                        {skill === 'listening' && <Headphones className="h-4 w-4" />}
                                                        {skill === 'reading' && <FileText className="h-4 w-4" />}
                                                        {skill === 'writing' && <PenTool className="h-4 w-4" />}
                                                        {skill === 'speaking' && <Mic className="h-4 w-4" />}
                                                        <span className="text-sm text-muted-foreground">
                                                            {skill === 'listening' && '30 min'}
                                                            {skill === 'reading' && '60 min'}
                                                            {skill === 'writing' && '60 min'}
                                                            {skill === 'speaking' && '11 min'}
                                                        </span>
                                                    </div>
                                                </Card>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-8">
                                    <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
                                    <p>Loading exam templates...</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="results" className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Generated Exams</CardTitle>
                            <CardDescription>
                                View and manage your generated exams
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="text-center py-8 text-muted-foreground">
                                <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                                <p>No exams generated yet. Create your first exam to see it here.</p>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
}
