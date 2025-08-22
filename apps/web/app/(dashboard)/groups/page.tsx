"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  Users,
  MessageCircle,
  Plus,
  Search,
  Filter,
  Calendar,
  Clock,
  Target,
  Trophy,
  Star,
  MessageSquare,
  ThumbsUp,
  Share2,
  MoreHorizontal
} from "lucide-react";

interface GroupMember {
  id: string;
  name: string;
  avatar: string;
  role: "admin" | "moderator" | "member";
  target_score: number;
  current_score: number;
  join_date: string;
  isOnline: boolean;
}

interface GroupPost {
  id: string;
  author: GroupMember;
  content: string;
  timestamp: string;
  likes: number;
  comments: number;
  type: "discussion" | "question" | "achievement" | "resource";
  tags: string[];
}

interface StudyGroup {
  id: string;
  name: string;
  description: string;
  avatar: string;
  member_count: number;
  max_members: number;
  target_score_range: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  isPublic: boolean;
  created_date: string;
  last_activity: string;
  members: GroupMember[];
  posts: GroupPost[];
}

const mockGroups: StudyGroup[] = [
  {
    id: "group-1",
    name: "IELTS Band 7+ Achievers",
    description: "A group for students targeting band 7 and above. Share strategies, practice together, and motivate each other.",
    avatar: "/api/avatars/group-1.png",
    member_count: 45,
    max_members: 50,
    target_score_range: "7.0-9.0",
    difficulty: "advanced",
    isPublic: true,
    created_date: "2024-01-01",
    last_activity: "2024-01-22T10:30:00Z",
    members: [
      {
        id: "user-1",
        name: "Sarah Johnson",
        avatar: "/api/avatars/sarah.png",
        role: "admin",
        target_score: 7.5,
        current_score: 7.2,
        join_date: "2024-01-01",
        isOnline: true
      },
      {
        id: "user-2",
        name: "Michael Chen",
        avatar: "/api/avatars/michael.png",
        role: "moderator",
        target_score: 8.0,
        current_score: 7.8,
        join_date: "2024-01-05",
        isOnline: false
      },
      {
        id: "user-3",
        name: "Emma Davis",
        avatar: "/api/avatars/emma.png",
        role: "member",
        target_score: 7.0,
        current_score: 6.8,
        join_date: "2024-01-10",
        isOnline: true
      }
    ],
    posts: [
      {
        id: "post-1",
        author: {
          id: "user-1",
          name: "Sarah Johnson",
          avatar: "/api/avatars/sarah.png",
          role: "admin",
          target_score: 7.5,
          current_score: 7.2,
          join_date: "2024-01-01",
          isOnline: true
        },
        content: "Just achieved my target score of 7.5! 🎉 The speaking practice sessions really helped. Anyone want to join our next group speaking practice?",
        timestamp: "2024-01-22T10:30:00Z",
        likes: 12,
        comments: 5,
        type: "achievement",
        tags: ["speaking", "success", "practice"]
      },
      {
        id: "post-2",
        author: {
          id: "user-2",
          name: "Michael Chen",
          avatar: "/api/avatars/michael.png",
          role: "moderator",
          target_score: 8.0,
          current_score: 7.8,
          join_date: "2024-01-05",
          isOnline: false
        },
        content: "I found this great resource for academic writing. It has sample essays with detailed feedback. Check it out: [link]",
        timestamp: "2024-01-22T09:15:00Z",
        likes: 8,
        comments: 3,
        type: "resource",
        tags: ["writing", "resources", "academic"]
      }
    ]
  },
  {
    id: "group-2",
    name: "IELTS Beginners Support",
    description: "New to IELTS? Join our supportive community for beginners. We help each other understand the basics and build confidence.",
    avatar: "/api/avatars/group-2.png",
    member_count: 78,
    max_members: 100,
    target_score_range: "5.0-6.5",
    difficulty: "beginner",
    isPublic: true,
    created_date: "2024-01-05",
    last_activity: "2024-01-22T11:45:00Z",
    members: [],
    posts: []
  },
  {
    id: "group-3",
    name: "IELTS Writing Masters",
    description: "Focus on improving your writing skills. Share essays, get feedback, and learn from each other's mistakes.",
    avatar: "/api/avatars/group-3.png",
    member_count: 32,
    max_members: 40,
    target_score_range: "6.5-8.0",
    difficulty: "intermediate",
    isPublic: true,
    created_date: "2024-01-10",
    last_activity: "2024-01-22T08:20:00Z",
    members: [],
    posts: []
  }
];

export default function GroupsPage() {
  const [selectedGroup, setSelectedGroup] = useState<StudyGroup | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterDifficulty, setFilterDifficulty] = useState<string>("all");
  const [newPostContent, setNewPostContent] = useState("");

  const filteredGroups = mockGroups.filter(group => {
    const matchesSearch = group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         group.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDifficulty = filterDifficulty === "all" || group.difficulty === filterDifficulty;
    return matchesSearch && matchesDifficulty;
  });

  const handleJoinGroup = (groupId: string) => {
    // In a real app, this would make an API call
    console.log(`Joining group ${groupId}`);
  };

  const handleCreatePost = () => {
    if (!newPostContent.trim() || !selectedGroup) return;
    
    // In a real app, this would make an API call
    console.log("Creating new post:", newPostContent);
    setNewPostContent("");
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const postTime = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - postTime.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "beginner": return "bg-green-100 text-green-800";
      case "intermediate": return "bg-yellow-100 text-yellow-800";
      case "advanced": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Study Groups</h1>
        <p className="text-muted-foreground">Connect with other IELTS students, share experiences, and learn together</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Groups List */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Find Groups
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search groups..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Filters */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Difficulty Level</label>
                <select
                  value={filterDifficulty}
                  onChange={(e) => setFilterDifficulty(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="all">All Levels</option>
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </select>
              </div>

              <Button className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Create New Group
              </Button>
            </CardContent>
          </Card>

          {/* Groups List */}
          <div className="space-y-4">
            {filteredGroups.map((group) => (
              <Card 
                key={group.id}
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedGroup?.id === group.id ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => setSelectedGroup(group)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Avatar className="w-12 h-12">
                      <AvatarImage src={group.avatar} />
                      <AvatarFallback>{group.name.charAt(0)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold text-lg truncate">{group.name}</h3>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {group.description}
                      </p>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge className={getDifficultyColor(group.difficulty)}>
                          {group.difficulty}
                        </Badge>
                        <span className="text-sm text-muted-foreground">
                          {group.member_count}/{group.max_members} members
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mt-2">
                        <Target className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">
                          Target: {group.target_score_range}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Group Details */}
        <div className="lg:col-span-2">
          {selectedGroup ? (
            <div className="space-y-6">
              {/* Group Header */}
              <Card>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-4">
                      <Avatar className="w-16 h-16">
                        <AvatarImage src={selectedGroup.avatar} />
                        <AvatarFallback>{selectedGroup.name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <CardTitle className="text-2xl">{selectedGroup.name}</CardTitle>
                        <CardDescription className="text-base">
                          {selectedGroup.description}
                        </CardDescription>
                        <div className="flex items-center gap-4 mt-2">
                          <Badge className={getDifficultyColor(selectedGroup.difficulty)}>
                            {selectedGroup.difficulty}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {selectedGroup.member_count} members
                          </span>
                          <span className="text-sm text-muted-foreground">
                            Created {new Date(selectedGroup.created_date).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <Button onClick={() => handleJoinGroup(selectedGroup.id)}>
                      Join Group
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              {/* Members */}
              <Card>
                <CardHeader>
                  <CardTitle>Members</CardTitle>
                  <CardDescription>Active members in this group</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {selectedGroup.members.map((member) => (
                      <div key={member.id} className="flex items-center gap-3 p-3 border rounded-lg">
                        <div className="relative">
                          <Avatar>
                            <AvatarImage src={member.avatar} />
                            <AvatarFallback>{member.name.charAt(0)}</AvatarFallback>
                          </Avatar>
                          {member.isOnline && (
                            <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium truncate">{member.name}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs">
                              {member.role}
                            </Badge>
                            <span className="text-xs text-muted-foreground">
                              {member.current_score.toFixed(1)} → {member.target_score.toFixed(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Posts */}
              <Card>
                <CardHeader>
                  <CardTitle>Discussion</CardTitle>
                  <CardDescription>Share your thoughts and questions</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* New Post */}
                  <div className="border rounded-lg p-4">
                    <textarea
                      placeholder="Share something with the group..."
                      value={newPostContent}
                      onChange={(e) => setNewPostContent(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={3}
                    />
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <MessageSquare className="w-4 h-4 mr-1" />
                          Discussion
                        </Button>
                        <Button variant="outline" size="sm">
                          <MessageSquare className="w-4 h-4 mr-1" />
                          Question
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trophy className="w-4 h-4 mr-1" />
                          Achievement
                        </Button>
                      </div>
                      <Button onClick={handleCreatePost} disabled={!newPostContent.trim()}>
                        Post
                      </Button>
                    </div>
                  </div>

                  {/* Posts List */}
                  <div className="space-y-4">
                    {selectedGroup.posts.map((post) => (
                      <div key={post.id} className="border rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <Avatar>
                            <AvatarImage src={post.author.avatar} />
                            <AvatarFallback>{post.author.name.charAt(0)}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h4 className="font-medium">{post.author.name}</h4>
                              <Badge variant="outline" className="text-xs">
                                {post.author.role}
                              </Badge>
                              <span className="text-sm text-muted-foreground">
                                {formatTimeAgo(post.timestamp)}
                              </span>
                            </div>
                            <p className="text-gray-700 mb-3">{post.content}</p>
                            <div className="flex items-center gap-4">
                              <Button variant="ghost" size="sm">
                                <ThumbsUp className="w-4 h-4 mr-1" />
                                {post.likes}
                              </Button>
                              <Button variant="ghost" size="sm">
                                <MessageCircle className="w-4 h-4 mr-1" />
                                {post.comments}
                              </Button>
                              <Button variant="ghost" size="sm">
                                <Share2 className="w-4 h-4 mr-1" />
                                Share
                              </Button>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">Select a Group</h3>
                <p className="text-muted-foreground">
                  Choose a study group from the list to view discussions and connect with other students.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
