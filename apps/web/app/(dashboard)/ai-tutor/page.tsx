'use client'

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { 
  MessageCircle, 
  Send, 
  Mic, 
  MicOff, 
  Lightbulb, 
  Target, 
  TrendingUp,
  BookOpen,
  Clock,
  Star,
  CheckCircle,
  PlayCircle,
  PauseCircle
} from 'lucide-react'

interface ChatMessage {
  id: string
  type: 'user' | 'tutor'
  message: string
  timestamp: Date
  suggestions?: string[]
  followUpQuestions?: string[]
  learningObjectives?: string[]
}

interface Recommendation {
  id: string
  title: string
  description: string
  type: 'content' | 'practice' | 'review' | 'challenge'
  priority: number
  estimatedTime: number
  reasoning: string
  expectedBenefit: string
  tags: string[]
}

interface LearningPath {
  id: string
  name: string
  description: string
  targetScore: number
  currentScore: number
  progress: number
  estimatedDays: number
  steps: LearningStep[]
}

interface LearningStep {
  id: string
  title: string
  description: string
  type: 'lesson' | 'practice' | 'quiz' | 'assessment'
  duration: number
  status: 'pending' | 'in_progress' | 'completed'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

export default function AITutorPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([])
  const [activeTab, setActiveTab] = useState('chat')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null)

  // Mock data for development
  useEffect(() => {
    // Initialize with welcome message
    setMessages([
      {
        id: '1',
        type: 'tutor',
        message: "Hello! I'm your AI IELTS tutor. I'm here to help you improve your English skills and achieve your target score. How can I assist you today?",
        timestamp: new Date(),
        suggestions: ['Start a practice test', 'Review weak areas', 'Set learning goals'],
        followUpQuestions: ["What's your current IELTS score?", "Which module do you find most challenging?"],
        learningObjectives: ['Establish learning baseline', 'Identify focus areas']
      }
    ])

    // Mock recommendations
    setRecommendations([
      {
        id: '1',
        title: 'Speaking Part 2 Practice',
        description: 'Practice describing topics with detailed vocabulary',
        type: 'practice',
        priority: 1,
        estimatedTime: 30,
        reasoning: 'Based on your recent speaking performance, you need more practice with extended responses.',
        expectedBenefit: 'Improve fluency and vocabulary range',
        tags: ['speaking', 'part2', 'fluency']
      },
      {
        id: '2',
        title: 'Academic Vocabulary Builder',
        description: 'Learn advanced academic vocabulary for writing',
        type: 'content',
        priority: 2,
        estimatedTime: 45,
        reasoning: 'Your writing scores show room for improvement in lexical resource.',
        expectedBenefit: 'Enhance essay vocabulary and sophistication',
        tags: ['writing', 'vocabulary', 'academic']
      },
      {
        id: '3',
        title: 'Reading Speed Techniques',
        description: 'Master skimming and scanning strategies',
        type: 'content',
        priority: 3,
        estimatedTime: 25,
        reasoning: 'Your reading speed could be improved to handle time constraints better.',
        expectedBenefit: 'Read faster while maintaining accuracy',
        tags: ['reading', 'speed', 'strategies']
      }
    ])

    // Mock learning paths
    setLearningPaths([
      {
        id: '1',
        name: 'Quick Improvement Path',
        description: 'Intensive 2-week program to boost your score',
        targetScore: 7.0,
        currentScore: 6.0,
        progress: 35,
        estimatedDays: 14,
        steps: [
          {
            id: '1',
            title: 'Speaking Fundamentals',
            description: 'Build confidence in basic speaking tasks',
            type: 'lesson',
            duration: 30,
            status: 'completed',
            difficulty: 'beginner'
          },
          {
            id: '2',
            title: 'Speaking Practice Session',
            description: 'Practice Part 1 and Part 2 questions',
            type: 'practice',
            duration: 45,
            status: 'in_progress',
            difficulty: 'intermediate'
          },
          {
            id: '3',
            title: 'Writing Structure Mastery',
            description: 'Learn essay structure and organization',
            type: 'lesson',
            duration: 60,
            status: 'pending',
            difficulty: 'intermediate'
          }
        ]
      }
    ])
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      message: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    // Mock AI response
    setTimeout(() => {
      const tutorResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'tutor',
        message: getMockResponse(inputMessage),
        timestamp: new Date(),
        suggestions: ['Continue practicing', 'Review grammar rules', 'Take a break'],
        followUpQuestions: ['How do you feel about your progress?', 'What specific area would you like to focus on?'],
        learningObjectives: ['Maintain consistency', 'Build confidence']
      }
      setMessages(prev => [...prev, tutorResponse])
      setIsLoading(false)
    }, 1000)
  }

  const getMockResponse = (message: string): string => {
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.includes('speaking') || lowerMessage.includes('talk')) {
      return "Great question about speaking! Speaking is often the most challenging module. Let me help you improve your speaking skills. I can provide practice questions, pronunciation tips, and fluency exercises. What specific aspect of speaking would you like to work on?"
    } else if (lowerMessage.includes('writing') || lowerMessage.includes('essay')) {
      return "Writing requires practice and understanding of the assessment criteria. I can help you with Task 1 (Academic/General) and Task 2 essay writing, including structure, vocabulary, and grammar. Would you like to practice a specific type of essay?"
    } else if (lowerMessage.includes('reading') || lowerMessage.includes('comprehension')) {
      return "Reading is about speed and accuracy. I can help you with skimming, scanning, and detailed reading strategies. We can practice with different types of passages and question formats. What reading skills would you like to improve?"
    } else if (lowerMessage.includes('listening') || lowerMessage.includes('audio')) {
      return "Listening requires practice with different accents and note-taking skills. I can provide audio materials and help you develop effective listening strategies. Would you like to practice with a specific type of listening task?"
    } else {
      return "I understand you're working on your IELTS preparation. I'm here to provide personalized guidance, practice materials, and feedback to help you achieve your target score. What specific area would you like to focus on today?"
    }
  }

  const toggleRecording = () => {
    setIsRecording(!isRecording)
    // In production, this would handle actual voice recording
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Tutor</h1>
          <p className="text-muted-foreground">Your personalized IELTS learning assistant</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="secondary" className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            Online
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageCircle className="w-4 h-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            Recommendations
          </TabsTrigger>
          <TabsTrigger value="learning-paths" className="flex items-center gap-2">
            <Target className="w-4 h-4" />
            Learning Paths
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Avatar className="w-8 h-8">
                  <AvatarImage src="/ai-tutor-avatar.png" />
                  <AvatarFallback>AI</AvatarFallback>
                </Avatar>
                AI Tutor Chat
              </CardTitle>
              <CardDescription>
                Ask questions, get personalized feedback, and practice your IELTS skills
              </CardDescription>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <ScrollArea className="flex-1 mb-4">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                        <div className={`rounded-lg p-3 ${
                          message.type === 'user' 
                            ? 'bg-primary text-primary-foreground' 
                            : 'bg-muted'
                        }`}>
                          <p className="text-sm">{message.message}</p>
                          <p className="text-xs opacity-70 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                        
                        {message.type === 'tutor' && message.suggestions && (
                          <div className="mt-2 space-y-2">
                            <p className="text-xs font-medium text-muted-foreground">Suggestions:</p>
                            <div className="flex flex-wrap gap-1">
                              {message.suggestions.map((suggestion, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {suggestion}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                      <Avatar className={`w-8 h-8 ${message.type === 'user' ? 'order-1' : 'order-2'}`}>
                        <AvatarImage src={message.type === 'user' ? '/user-avatar.png' : '/ai-tutor-avatar.png'} />
                        <AvatarFallback>{message.type === 'user' ? 'U' : 'AI'}</AvatarFallback>
                      </Avatar>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted rounded-lg p-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
              
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={toggleRecording}
                  className={isRecording ? 'bg-red-100 text-red-600' : ''}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </Button>
                <Input
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  className="flex-1"
                />
                <Button onClick={sendMessage} disabled={!inputMessage.trim() || isLoading}>
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {recommendations.map((recommendation) => (
              <Card key={recommendation.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Badge variant={
                      recommendation.type === 'practice' ? 'default' :
                      recommendation.type === 'content' ? 'secondary' :
                      recommendation.type === 'review' ? 'outline' : 'destructive'
                    }>
                      {recommendation.type}
                    </Badge>
                    <div className="flex items-center gap-1">
                      {[...Array(recommendation.priority)].map((_, i) => (
                        <Star key={i} className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      ))}
                    </div>
                  </div>
                  <CardTitle className="text-lg">{recommendation.title}</CardTitle>
                  <CardDescription>{recommendation.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Clock className="w-4 h-4" />
                    {recommendation.estimatedTime} minutes
                  </div>
                  <p className="text-sm">{recommendation.reasoning}</p>
                  <div className="flex flex-wrap gap-1">
                    {recommendation.tags.map((tag, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <Button className="w-full" size="sm">
                    Start {recommendation.type}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="learning-paths" className="space-y-4">
          {learningPaths.map((path) => (
            <Card key={path.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{path.name}</CardTitle>
                    <CardDescription>{path.description}</CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{path.targetScore}</div>
                    <div className="text-sm text-muted-foreground">Target Score</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{path.progress}%</span>
                  </div>
                  <Progress value={path.progress} className="w-full" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span>Current Score: {path.currentScore}</span>
                    <span>Estimated: {path.estimatedDays} days</span>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-3">
                    <h4 className="font-medium">Learning Steps</h4>
                    {path.steps.map((step) => (
                      <div key={step.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            step.status === 'completed' ? 'bg-green-100 text-green-600' :
                            step.status === 'in_progress' ? 'bg-blue-100 text-blue-600' :
                            'bg-gray-100 text-gray-600'
                          }`}>
                            {step.status === 'completed' ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : step.status === 'in_progress' ? (
                              <PlayCircle className="w-4 h-4" />
                            ) : (
                              <PauseCircle className="w-4 h-4" />
                            )}
                          </div>
                          <div>
                            <p className="font-medium">{step.title}</p>
                            <p className="text-sm text-muted-foreground">{step.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{step.difficulty}</Badge>
                          <span className="text-sm text-muted-foreground">{step.duration}m</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
  )
}
