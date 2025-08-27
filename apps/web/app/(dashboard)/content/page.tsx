"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Bookmark,
    BookOpen,
    Clock,
    Code,
    Edit,
    Eye,
    Filter,
    Headphones,
    Mic,
    PenTool,
    Play,
    Plus,
    Search,
    Star,
    Trash2
} from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

interface ContentItem {
    id: string;
    title: string;
    content_type: string;
    difficulty_level: string;
    status: string;
    category?: {
        name: string;
        color: string;
    };
    created_at: string;
    estimated_time?: number;
    word_count?: number;
    target_band_score?: number;
    usage_count?: number;
    average_rating?: number;
}

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

const statusOptions = [
    { value: "draft", label: "Draft" },
    { value: "published", label: "Published" },
    { value: "archived", label: "Archived" },
    { value: "under_review", label: "Under Review" },
];

export default function ContentManagementPage() {
    const [contentItems, setContentItems] = useState<ContentItem[]>([]);
    const [categories, setCategories] = useState<ContentCategory[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedType, setSelectedType] = useState<string>("");
    const [selectedDifficulty, setSelectedDifficulty] = useState<string>("");
    const [selectedStatus, setSelectedStatus] = useState<string>("");
    const [selectedCategory, setSelectedCategory] = useState<string>("");
    const [activeTab, setActiveTab] = useState("all");

    useEffect(() => {
        fetchContentItems();
        fetchCategories();
    }, []);

    const fetchContentItems = async () => {
        try {
            const params = new URLSearchParams();
            if (searchTerm) params.append("search", searchTerm);
            if (selectedType) params.append("content_type", selectedType);
            if (selectedDifficulty) params.append("difficulty_level", selectedDifficulty);
            if (selectedStatus) params.append("status", selectedStatus);
            if (selectedCategory) params.append("category_id", selectedCategory);

            const response = await fetch(`/api/content/items?${params.toString()}`);
            if (response.ok) {
                const data = await response.json();
                setContentItems(data);
            }
        } catch (error) {
            console.error("Error fetching content items:", error);
        } finally {
            setLoading(false);
        }
    };

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

    const handleSearch = () => {
        fetchContentItems();
    };

    const handleClearFilters = () => {
        setSearchTerm("");
        setSelectedType("");
        setSelectedDifficulty("");
        setSelectedStatus("");
        setSelectedCategory("");
        fetchContentItems();
    };

    const getContentTypeIcon = (type: string) => {
        const contentType = contentTypes.find(t => t.value === type);
        return contentType ? contentType.icon : BookOpen;
    };

    const getContentTypeLabel = (type: string) => {
        const contentType = contentTypes.find(t => t.value === type);
        return contentType ? contentType.label : "Unknown";
    };

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case "beginner": return "bg-green-100 text-green-800";
            case "elementary": return "bg-blue-100 text-blue-800";
            case "intermediate": return "bg-yellow-100 text-yellow-800";
            case "upper_intermediate": return "bg-orange-100 text-orange-800";
            case "advanced": return "bg-red-100 text-red-800";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case "published": return "bg-green-100 text-green-800";
            case "draft": return "bg-gray-100 text-gray-800";
            case "archived": return "bg-red-100 text-red-800";
            case "under_review": return "bg-yellow-100 text-yellow-800";
            default: return "bg-gray-100 text-gray-800";
        }
    };

    const filteredContent = contentItems.filter(item => {
        if (activeTab === "all") return true;
        if (activeTab === "published") return item.status === "published";
        if (activeTab === "draft") return item.status === "draft";
        if (activeTab === "archived") return item.status === "archived";
        return true;
    });

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
            </div>
        );
    }

    return (
        <div className="container mx-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold">Content Management</h1>
                    <p className="text-gray-600">Manage your IELTS learning content</p>
                </div>
                <Link href="/content/create">
                    <Button className="flex items-center gap-2">
                        <Plus className="h-4 w-4" />
                        Create Content
                    </Button>
                </Link>
            </div>

            {/* Filters */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Filter className="h-5 w-5" />
                        Filters & Search
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                        <div className="relative">
                            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                            <Input
                                placeholder="Search content..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="pl-10"
                            />
                        </div>
                        <Select value={selectedType} onValueChange={setSelectedType}>
                            <SelectTrigger>
                                <SelectValue placeholder="Content Type" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="">All Types</SelectItem>
                                {contentTypes.map((type) => (
                                    <SelectItem key={type.value} value={type.value}>
                                        {type.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
                            <SelectTrigger>
                                <SelectValue placeholder="Difficulty" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="">All Levels</SelectItem>
                                {difficultyLevels.map((level) => (
                                    <SelectItem key={level.value} value={level.value}>
                                        {level.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                            <SelectTrigger>
                                <SelectValue placeholder="Status" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="">All Status</SelectItem>
                                {statusOptions.map((status) => (
                                    <SelectItem key={status.value} value={status.value}>
                                        {status.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                            <SelectTrigger>
                                <SelectValue placeholder="Category" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="">All Categories</SelectItem>
                                {categories.map((category) => (
                                    <SelectItem key={category.id} value={category.id}>
                                        {category.name}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="flex gap-2">
                        <Button onClick={handleSearch}>Apply Filters</Button>
                        <Button variant="outline" onClick={handleClearFilters}>
                            Clear Filters
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Content Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-4">
                    <TabsTrigger value="all">All Content</TabsTrigger>
                    <TabsTrigger value="published">Published</TabsTrigger>
                    <TabsTrigger value="draft">Draft</TabsTrigger>
                    <TabsTrigger value="archived">Archived</TabsTrigger>
                </TabsList>

                <TabsContent value={activeTab} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredContent.map((item) => {
                            const IconComponent = getContentTypeIcon(item.content_type);
                            return (
                                <Card key={item.id} className="hover:shadow-lg transition-shadow">
                                    <CardHeader className="pb-3">
                                        <div className="flex items-start justify-between">
                                            <div className="flex items-center gap-2">
                                                <IconComponent className="h-5 w-5 text-blue-600" />
                                                <Badge variant="outline" className={getDifficultyColor(item.difficulty_level)}>
                                                    {item.difficulty_level}
                                                </Badge>
                                            </div>
                                            <Badge className={getStatusColor(item.status)}>
                                                {item.status}
                                            </Badge>
                                        </div>
                                        <CardTitle className="text-lg">{item.title}</CardTitle>
                                        {item.category && (
                                            <Badge
                                                variant="outline"
                                                style={{ backgroundColor: item.category.color + '20', color: item.category.color }}
                                            >
                                                {item.category.name}
                                            </Badge>
                                        )}
                                    </CardHeader>
                                    <CardContent className="space-y-3">
                                        <div className="flex items-center justify-between text-sm text-gray-600">
                                            <div className="flex items-center gap-4">
                                                {item.estimated_time && (
                                                    <div className="flex items-center gap-1">
                                                        <Clock className="h-4 w-4" />
                                                        <span>{item.estimated_time} min</span>
                                                    </div>
                                                )}
                                                {item.word_count && (
                                                    <div className="flex items-center gap-1">
                                                        <BookOpen className="h-4 w-4" />
                                                        <span>{item.word_count} words</span>
                                                    </div>
                                                )}
                                            </div>
                                            {item.average_rating && (
                                                <div className="flex items-center gap-1">
                                                    <Star className="h-4 w-4 text-yellow-500" />
                                                    <span>{item.average_rating.toFixed(1)}</span>
                                                </div>
                                            )}
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-1 text-sm text-gray-600">
                                                <Eye className="h-4 w-4" />
                                                <span>{item.usage_count || 0} views</span>
                                            </div>
                                            <div className="flex gap-2">
                                                <Link href={`/content/${item.id}`}>
                                                    <Button size="sm" variant="outline">
                                                        <Play className="h-4 w-4" />
                                                    </Button>
                                                </Link>
                                                <Link href={`/content/${item.id}/edit`}>
                                                    <Button size="sm" variant="outline">
                                                        <Edit className="h-4 w-4" />
                                                    </Button>
                                                </Link>
                                                <Button size="sm" variant="outline" className="text-red-600 hover:text-red-700">
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            );
                        })}
                    </div>

                    {filteredContent.length === 0 && (
                        <div className="text-center py-12">
                            <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
                            <p className="text-gray-600 mb-4">
                                {activeTab === "all"
                                    ? "No content items match your current filters."
                                    : `No ${activeTab} content items found.`
                                }
                            </p>
                            <Link href="/content/create">
                                <Button>Create Your First Content</Button>
                            </Link>
                        </div>
                    )}
                </TabsContent>
            </Tabs>
        </div>
    );
}
