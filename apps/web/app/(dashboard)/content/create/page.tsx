"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
    ArrowLeft,
    Bookmark,
    BookOpen,
    Code,
    Eye,
    Headphones,
    Mic,
    PenTool,
    Plus,
    Save,
    X
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface ContentCategory {
    id: string;
    name: string;
    description?: string;
    color: string;
    icon: string;
}

const contentTypes = [
    { value: "reading_passage", label: "Reading Passage", icon: BookOpen },
    { value: "listening_audio", label: "Listening Audio", icon: Headphones },
    { value: "writing_prompt", label: "Writing Prompt", icon: PenTool },
    { value: "speaking_topic", label: "Speaking Topic", icon: Mic },
    { value: "grammar_lesson", label: "Grammar Lesson", icon: Code },
    { value: "vocabulary_lesson", label: "Vocabulary Lesson", icon: Bookmark },
];

const difficultyLevels = [
    { value: "beginner", label: "Beginner" },
    { value: "elementary", label: "Elementary" },
    { value: "intermediate", label: "Intermediate" },
    { value: "upper_intermediate", label: "Upper Intermediate" },
    { value: "advanced", label: "Advanced" },
];

interface ContentFormData {
    title: string;
    content_type: string;
    difficulty_level: string;
    category_id: string;
    content_text: string;
    audio_url: string;
    audio_duration: number;
    transcript: string;
    prompt: string;
    sample_answer: string;
    vocabulary_list: { [key: string]: string };
    grammar_points: string[];
    tags: string[];
    estimated_time: number;
    word_count: number;
    target_band_score: number;
}

export default function CreateContentPage() {
    const router = useRouter();
    const [categories, setCategories] = useState<ContentCategory[]>([]);
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState("basic");
    const [newTag, setNewTag] = useState("");
    const [newVocabulary, setNewVocabulary] = useState({ word: "", definition: "" });
    const [newGrammarPoint, setNewGrammarPoint] = useState("");

    const [formData, setFormData] = useState<ContentFormData>({
        title: "",
        content_type: "",
        difficulty_level: "",
        category_id: "",
        content_text: "",
        audio_url: "",
        audio_duration: 0,
        transcript: "",
        prompt: "",
        sample_answer: "",
        vocabulary_list: {},
        grammar_points: [],
        tags: [],
        estimated_time: 0,
        word_count: 0,
        target_band_score: 0,
    });

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await fetch("/api/content/categories");
            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            }
        } catch (error) {
            console.error("Error fetching categories:", error);
        }
    };

    const handleInputChange = (field: keyof ContentFormData, value: any) => {
        setFormData(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const addTag = () => {
        if (newTag.trim() && !formData.tags.includes(newTag.trim())) {
            setFormData(prev => ({
                ...prev,
                tags: [...prev.tags, newTag.trim()]
            }));
            setNewTag("");
        }
    };

    const removeTag = (tagToRemove: string) => {
        setFormData(prev => ({
            ...prev,
            tags: prev.tags.filter(tag => tag !== tagToRemove)
        }));
    };

    const addVocabulary = () => {
        if (newVocabulary.word.trim() && newVocabulary.definition.trim()) {
            setFormData(prev => ({
                ...prev,
                vocabulary_list: {
                    ...prev.vocabulary_list,
                    [newVocabulary.word.trim()]: newVocabulary.definition.trim()
                }
            }));
            setNewVocabulary({ word: "", definition: "" });
        }
    };

    const removeVocabulary = (word: string) => {
        setFormData(prev => {
            const newVocabularyList = { ...prev.vocabulary_list };
            delete newVocabularyList[word];
            return {
                ...prev,
                vocabulary_list: newVocabularyList
            };
        });
    };

    const addGrammarPoint = () => {
        if (newGrammarPoint.trim() && !formData.grammar_points.includes(newGrammarPoint.trim())) {
            setFormData(prev => ({
                ...prev,
                grammar_points: [...prev.grammar_points, newGrammarPoint.trim()]
            }));
            setNewGrammarPoint("");
        }
    };

    const removeGrammarPoint = (pointToRemove: string) => {
        setFormData(prev => ({
            ...prev,
            grammar_points: prev.grammar_points.filter(point => point !== pointToRemove)
        }));
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            const response = await fetch("/api/content/items", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const data = await response.json();
                router.push(`/content/${data.id}`);
            } else {
                console.error("Error creating content:", await response.text());
            }
        } catch (error) {
            console.error("Error creating content:", error);
        } finally {
            setLoading(false);
        }
    };

    const getContentTypeIcon = (type: string) => {
        const contentType = contentTypes.find(t => t.value === type);
        return contentType ? contentType.icon : BookOpen;
    };

    const isFormValid = () => {
        return (
            formData.title.trim() &&
            formData.content_type &&
            formData.difficulty_level &&
            formData.category_id
        );
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Link href="/content">
                        <Button variant="outline" size="sm">
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Content
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-3xl font-bold">Create New Content</h1>
                        <p className="text-gray-600">Add new learning content to your library</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={() => router.push("/content")}>
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSubmit}
                        disabled={!isFormValid() || loading}
                        className="flex items-center gap-2"
                    >
                        <Save className="h-4 w-4" />
                        {loading ? "Creating..." : "Create Content"}
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Form */}
                <div className="lg:col-span-2">
                    <Tabs value={activeTab} onValueChange={setActiveTab}>
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="basic">Basic Info</TabsTrigger>
                            <TabsTrigger value="content">Content</TabsTrigger>
                            <TabsTrigger value="metadata">Metadata</TabsTrigger>
                            <TabsTrigger value="preview">Preview</TabsTrigger>
                        </TabsList>

                        {/* Basic Information Tab */}
                        <TabsContent value="basic" className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Basic Information</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <Label htmlFor="title">Title *</Label>
                                        <Input
                                            id="title"
                                            value={formData.title}
                                            onChange={(e) => handleInputChange("title", e.target.value)}
                                            placeholder="Enter content title"
                                        />
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <Label htmlFor="content_type">Content Type *</Label>
                                            <Select value={formData.content_type} onValueChange={(value) => handleInputChange("content_type", value)}>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select content type" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {contentTypes.map((type) => {
                                                        const IconComponent = type.icon;
                                                        return (
                                                            <SelectItem key={type.value} value={type.value}>
                                                                <div className="flex items-center gap-2">
                                                                    <IconComponent className="h-4 w-4" />
                                                                    {type.label}
                                                                </div>
                                                            </SelectItem>
                                                        );
                                                    })}
                                                </SelectContent>
                                            </Select>
                                        </div>

                                        <div>
                                            <Label htmlFor="difficulty_level">Difficulty Level *</Label>
                                            <Select value={formData.difficulty_level} onValueChange={(value) => handleInputChange("difficulty_level", value)}>
                                                <SelectTrigger>
                                                    <SelectValue placeholder="Select difficulty" />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    {difficultyLevels.map((level) => (
                                                        <SelectItem key={level.value} value={level.value}>
                                                            {level.label}
                                                        </SelectItem>
                                                    ))}
                                                </SelectContent>
                                            </Select>
                                        </div>
                                    </div>

                                    <div>
                                        <Label htmlFor="category">Category *</Label>
                                        <Select value={formData.category_id} onValueChange={(value) => handleInputChange("category_id", value)}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="Select category" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {categories.map((category) => (
                                                    <SelectItem key={category.id} value={category.id}>
                                                        <div className="flex items-center gap-2">
                                                            <div
                                                                className="w-3 h-3 rounded-full"
                                                                style={{ backgroundColor: category.color }}
                                                            />
                                                            {category.name}
                                                        </div>
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div>
                                            <Label htmlFor="estimated_time">Estimated Time (minutes)</Label>
                                            <Input
                                                id="estimated_time"
                                                type="number"
                                                value={formData.estimated_time}
                                                onChange={(e) => handleInputChange("estimated_time", parseInt(e.target.value) || 0)}
                                                placeholder="30"
                                            />
                                        </div>

                                        <div>
                                            <Label htmlFor="word_count">Word Count</Label>
                                            <Input
                                                id="word_count"
                                                type="number"
                                                value={formData.word_count}
                                                onChange={(e) => handleInputChange("word_count", parseInt(e.target.value) || 0)}
                                                placeholder="500"
                                            />
                                        </div>

                                        <div>
                                            <Label htmlFor="target_band_score">Target Band Score</Label>
                                            <Input
                                                id="target_band_score"
                                                type="number"
                                                step="0.5"
                                                min="0"
                                                max="9"
                                                value={formData.target_band_score}
                                                onChange={(e) => handleInputChange("target_band_score", parseFloat(e.target.value) || 0)}
                                                placeholder="6.5"
                                            />
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* Content Tab */}
                        <TabsContent value="content" className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Content Details</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    {formData.content_type === "reading_passage" && (
                                        <div>
                                            <Label htmlFor="content_text">Reading Passage</Label>
                                            <Textarea
                                                id="content_text"
                                                value={formData.content_text}
                                                onChange={(e) => handleInputChange("content_text", e.target.value)}
                                                placeholder="Enter the reading passage text..."
                                                rows={10}
                                            />
                                        </div>
                                    )}

                                    {formData.content_type === "listening_audio" && (
                                        <>
                                            <div>
                                                <Label htmlFor="audio_url">Audio URL</Label>
                                                <Input
                                                    id="audio_url"
                                                    value={formData.audio_url}
                                                    onChange={(e) => handleInputChange("audio_url", e.target.value)}
                                                    placeholder="https://example.com/audio.mp3"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="audio_duration">Audio Duration (seconds)</Label>
                                                <Input
                                                    id="audio_duration"
                                                    type="number"
                                                    value={formData.audio_duration}
                                                    onChange={(e) => handleInputChange("audio_duration", parseInt(e.target.value) || 0)}
                                                    placeholder="180"
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="transcript">Transcript</Label>
                                                <Textarea
                                                    id="transcript"
                                                    value={formData.transcript}
                                                    onChange={(e) => handleInputChange("transcript", e.target.value)}
                                                    placeholder="Enter the audio transcript..."
                                                    rows={8}
                                                />
                                            </div>
                                        </>
                                    )}

                                    {formData.content_type === "writing_prompt" && (
                                        <>
                                            <div>
                                                <Label htmlFor="prompt">Writing Prompt</Label>
                                                <Textarea
                                                    id="prompt"
                                                    value={formData.prompt}
                                                    onChange={(e) => handleInputChange("prompt", e.target.value)}
                                                    placeholder="Enter the writing prompt..."
                                                    rows={4}
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="sample_answer">Sample Answer</Label>
                                                <Textarea
                                                    id="sample_answer"
                                                    value={formData.sample_answer}
                                                    onChange={(e) => handleInputChange("sample_answer", e.target.value)}
                                                    placeholder="Enter a sample answer..."
                                                    rows={8}
                                                />
                                            </div>
                                        </>
                                    )}

                                    {formData.content_type === "speaking_topic" && (
                                        <>
                                            <div>
                                                <Label htmlFor="prompt">Speaking Topic</Label>
                                                <Textarea
                                                    id="prompt"
                                                    value={formData.prompt}
                                                    onChange={(e) => handleInputChange("prompt", e.target.value)}
                                                    placeholder="Enter the speaking topic..."
                                                    rows={4}
                                                />
                                            </div>
                                            <div>
                                                <Label htmlFor="sample_answer">Sample Response</Label>
                                                <Textarea
                                                    id="sample_answer"
                                                    value={formData.sample_answer}
                                                    onChange={(e) => handleInputChange("sample_answer", e.target.value)}
                                                    placeholder="Enter a sample response..."
                                                    rows={8}
                                                />
                                            </div>
                                        </>
                                    )}

                                    {(formData.content_type === "grammar_lesson" || formData.content_type === "vocabulary_lesson") && (
                                        <div>
                                            <Label htmlFor="content_text">Lesson Content</Label>
                                            <Textarea
                                                id="content_text"
                                                value={formData.content_text}
                                                onChange={(e) => handleInputChange("content_text", e.target.value)}
                                                placeholder="Enter the lesson content..."
                                                rows={10}
                                            />
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* Metadata Tab */}
                        <TabsContent value="metadata" className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Tags & Keywords</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <Label>Tags</Label>
                                        <div className="flex gap-2 mb-2">
                                            <Input
                                                value={newTag}
                                                onChange={(e) => setNewTag(e.target.value)}
                                                placeholder="Add a tag"
                                                onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                                            />
                                            <Button onClick={addTag} size="sm">
                                                <Plus className="h-4 w-4" />
                                            </Button>
                                        </div>
                                        <div className="flex flex-wrap gap-2">
                                            {formData.tags.map((tag) => (
                                                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                                                    {tag}
                                                    <X
                                                        className="h-3 w-3 cursor-pointer"
                                                        onClick={() => removeTag(tag)}
                                                    />
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Vocabulary List</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                                        <Input
                                            value={newVocabulary.word}
                                            onChange={(e) => setNewVocabulary(prev => ({ ...prev, word: e.target.value }))}
                                            placeholder="Word"
                                        />
                                        <Input
                                            value={newVocabulary.definition}
                                            onChange={(e) => setNewVocabulary(prev => ({ ...prev, definition: e.target.value }))}
                                            placeholder="Definition"
                                        />
                                    </div>
                                    <Button onClick={addVocabulary} size="sm">
                                        <Plus className="h-4 w-4 mr-2" />
                                        Add Vocabulary
                                    </Button>
                                    <div className="space-y-2">
                                        {Object.entries(formData.vocabulary_list).map(([word, definition]) => (
                                            <div key={word} className="flex items-center justify-between p-2 border rounded">
                                                <div>
                                                    <strong>{word}</strong>: {definition}
                                                </div>
                                                <X
                                                    className="h-4 w-4 cursor-pointer text-red-500"
                                                    onClick={() => removeVocabulary(word)}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader>
                                    <CardTitle>Grammar Points</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="flex gap-2">
                                        <Input
                                            value={newGrammarPoint}
                                            onChange={(e) => setNewGrammarPoint(e.target.value)}
                                            placeholder="Add a grammar point"
                                            onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), addGrammarPoint())}
                                        />
                                        <Button onClick={addGrammarPoint} size="sm">
                                            <Plus className="h-4 w-4" />
                                        </Button>
                                    </div>
                                    <div className="space-y-2">
                                        {formData.grammar_points.map((point) => (
                                            <div key={point} className="flex items-center justify-between p-2 border rounded">
                                                <span>{point}</span>
                                                <X
                                                    className="h-4 w-4 cursor-pointer text-red-500"
                                                    onClick={() => removeGrammarPoint(point)}
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </CardContent>
                            </Card>
                        </TabsContent>

                        {/* Preview Tab */}
                        <TabsContent value="preview" className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Content Preview</CardTitle>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div className="flex items-center gap-2">
                                        {formData.content_type && (
                                            <>
                                                {(() => {
                                                    const IconComponent = getContentTypeIcon(formData.content_type);
                                                    return <IconComponent className="h-5 w-5 text-blue-600" />;
                                                })()}
                                                <Badge variant="outline">
                                                    {contentTypes.find(t => t.value === formData.content_type)?.label}
                                                </Badge>
                                            </>
                                        )}
                                        {formData.difficulty_level && (
                                            <Badge variant="outline">
                                                {difficultyLevels.find(l => l.value === formData.difficulty_level)?.label}
                                            </Badge>
                                        )}
                                    </div>

                                    <div>
                                        <h3 className="text-xl font-semibold">{formData.title || "Untitled"}</h3>
                                        {formData.category_id && (
                                            <p className="text-gray-600">
                                                Category: {categories.find(c => c.id === formData.category_id)?.name}
                                            </p>
                                        )}
                                    </div>

                                    {formData.content_text && (
                                        <div>
                                            <h4 className="font-medium mb-2">Content:</h4>
                                            <div className="p-4 border rounded bg-gray-50">
                                                {formData.content_text}
                                            </div>
                                        </div>
                                    )}

                                    {formData.prompt && (
                                        <div>
                                            <h4 className="font-medium mb-2">Prompt:</h4>
                                            <div className="p-4 border rounded bg-blue-50">
                                                {formData.prompt}
                                            </div>
                                        </div>
                                    )}

                                    {formData.tags.length > 0 && (
                                        <div>
                                            <h4 className="font-medium mb-2">Tags:</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {formData.tags.map((tag) => (
                                                    <Badge key={tag} variant="secondary">
                                                        {tag}
                                                    </Badge>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Content Statistics</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex justify-between">
                                <span>Word Count:</span>
                                <span className="font-medium">{formData.word_count}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Estimated Time:</span>
                                <span className="font-medium">{formData.estimated_time} min</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Tags:</span>
                                <span className="font-medium">{formData.tags.length}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Vocabulary:</span>
                                <span className="font-medium">{Object.keys(formData.vocabulary_list).length}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Grammar Points:</span>
                                <span className="font-medium">{formData.grammar_points.length}</span>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Quick Actions</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-2">
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => setActiveTab("basic")}
                            >
                                <Eye className="h-4 w-4 mr-2" />
                                Review Basic Info
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => setActiveTab("content")}
                            >
                                <BookOpen className="h-4 w-4 mr-2" />
                                Edit Content
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => setActiveTab("metadata")}
                            >
                                <Plus className="h-4 w-4 mr-2" />
                                Add Metadata
                            </Button>
                            <Button
                                variant="outline"
                                className="w-full justify-start"
                                onClick={() => setActiveTab("preview")}
                            >
                                <Eye className="h-4 w-4 mr-2" />
                                Preview Content
                            </Button>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
