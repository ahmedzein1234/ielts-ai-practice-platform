'use client'

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
    BarChart3,
    Bot,
    BrainCircuit,
    Clock,
    Headphones,
    MessageCircle,
    Mic,
    MicOff,
    PlayCircle,
    Send,
    Settings,
    Target,
    User,
    Volume2
} from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'

interface MultiModalMessage {
    id: string
    type: 'user' | 'tutor'
    content: {
        text?: string
        audio?: string
        visual?: string
        interactive?: any
        exercise?: any
        feedback?: any
    }
    responseType: 'text' | 'audio' | 'visual' | 'interactive' | 'exercise' | 'feedback'
    teachingStyle: 'exploratory' | 'structured' | 'conversational' | 'challenging' | 'supportive' | 'gamified'
    interactionMode: 'text' | 'voice' | 'gesture' | 'multi_modal'
    confidence: number
    timestamp: Date
}

interface SpeechAnalysis {
    pronunciation: number
    fluency: number
    grammar: number
    vocabulary: number
    overall: number
    feedback: string[]
    suggestions: string[]
}

interface TutorPersonality {
    teachingStyle: 'exploratory' | 'structured' | 'conversational' | 'challenging' | 'supportive' | 'gamified'
    interactionMode: 'text' | 'voice' | 'gesture' | 'multi_modal'
    difficultyLevel: 'beginner' | 'intermediate' | 'advanced'
    feedbackStyle: 'encouraging' | 'constructive' | 'detailed' | 'brief'
    pace: 'slow' | 'moderate' | 'fast'
}

interface EnhancedTutorInterfaceProps {
    userId: string
    onMessage?: (message: MultiModalMessage) => void
    onSpeechAnalysis?: (analysis: SpeechAnalysis) => void
    onPersonalityChange?: (personality: TutorPersonality) => void
}

export default function EnhancedTutorInterface({
    userId,
    onMessage,
    onSpeechAnalysis,
    onPersonalityChange
}: EnhancedTutorInterfaceProps) {
    const [messages, setMessages] = useState<MultiModalMessage[]>([])
    const [inputMessage, setInputMessage] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [isRecording, setIsRecording] = useState(false)
    const [audioLevel, setAudioLevel] = useState(0)
    const [speechAnalysis, setSpeechAnalysis] = useState<SpeechAnalysis | null>(null)
    const [tutorPersonality, setTutorPersonality] = useState<TutorPersonality>({
        teachingStyle: 'conversational',
        interactionMode: 'multi_modal',
        difficultyLevel: 'intermediate',
        feedbackStyle: 'constructive',
        pace: 'moderate'
    })
    const [activeTab, setActiveTab] = useState('chat')
    const [wsConnection, setWsConnection] = useState<WebSocket | null>(null)
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
    const [isTyping, setIsTyping] = useState(false)

    const messagesEndRef = useRef<HTMLDivElement>(null)
    const audioRef = useRef<HTMLAudioElement>(null)
    const mediaRecorderRef = useRef<MediaRecorder | null>(null)
    const audioContextRef = useRef<AudioContext | null>(null)
    const analyserRef = useRef<AnalyserNode | null>(null)
    const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

    // Initialize WebSocket connection
    useEffect(() => {
        const connectWebSocket = () => {
            setConnectionStatus('connecting')
            const ws = new WebSocket(`ws://localhost:8004/ws/tutor/${userId}`)

            ws.onopen = () => {
                setConnectionStatus('connected')
                setWsConnection(ws)
                console.log('Enhanced WebSocket connected')
            }

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data)
                handleWebSocketMessage(data)
            }

            ws.onclose = () => {
                setConnectionStatus('disconnected')
                setWsConnection(null)
                console.log('Enhanced WebSocket disconnected')
                setTimeout(connectWebSocket, 5000)
            }

            ws.onerror = (error) => {
                console.error('Enhanced WebSocket error:', error)
                setConnectionStatus('disconnected')
            }
        }

        connectWebSocket()

        return () => {
            if (wsConnection) {
                wsConnection.close()
            }
        }
    }, [userId])

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'tutor_response':
                const tutorMessage: MultiModalMessage = {
                    id: Date.now().toString(),
                    type: 'tutor',
                    content: data.data.content || { text: data.data.text || 'Response received' },
                    responseType: data.data.responseType || 'text',
                    teachingStyle: data.data.teachingStyle || 'conversational',
                    interactionMode: data.data.interactionMode || 'text',
                    confidence: data.data.confidence || 0.9,
                    timestamp: new Date()
                }
                setMessages(prev => [...prev, tutorMessage])
                setIsLoading(false)
                onMessage?.(tutorMessage)
                break

            case 'speech_analysis':
                setSpeechAnalysis(data.data)
                onSpeechAnalysis?.(data.data)
                break

            case 'audio_response':
                if (audioRef.current && data.data.audio) {
                    const audioData = atob(data.data.audio)
                    const audioBlob = new Blob([audioData], { type: 'audio/wav' })
                    audioRef.current.src = URL.createObjectURL(audioBlob)
                    audioRef.current.play()
                }
                break

            case 'typing_indicator':
                setIsTyping(data.data.is_typing)
                break

            case 'connection_status':
                setConnectionStatus(data.data.status)
                break

            default:
                console.log('Unknown message type:', data.type)
        }
    }

    // Initialize with welcome message
    useEffect(() => {
        setMessages([
            {
                id: '1',
                type: 'tutor',
                content: {
                    text: "Hello! I'm your enhanced AI IELTS tutor. I can help you with text, voice, and multi-modal interactions. I adapt my teaching style based on your preferences and progress. How would you like to start?"
                },
                responseType: 'text',
                teachingStyle: 'conversational',
                interactionMode: 'multi_modal',
                confidence: 0.95,
                timestamp: new Date()
            }
        ])
    }, [])

    const scrollToBottom = useCallback(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [])

    useEffect(() => {
        scrollToBottom()
    }, [messages, scrollToBottom])

    const sendMessage = async () => {
        if (!inputMessage.trim() || !wsConnection) return

        const userMessage: MultiModalMessage = {
            id: Date.now().toString(),
            type: 'user',
            content: { text: inputMessage },
            responseType: 'text',
            teachingStyle: tutorPersonality.teachingStyle,
            interactionMode: tutorPersonality.interactionMode,
            confidence: 1.0,
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInputMessage('')
        setIsLoading(true)
        onMessage?.(userMessage)

        // Send via WebSocket
        wsConnection.send(JSON.stringify({
            type: 'user_message',
            message: inputMessage,
            personality: tutorPersonality
        }))
    }

    const startVoiceRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            mediaRecorderRef.current = new MediaRecorder(stream)

            // Set up audio analysis
            audioContextRef.current = new AudioContext()
            const source = audioContextRef.current.createMediaStreamSource(stream)
            analyserRef.current = audioContextRef.current.createAnalyser()
            source.connect(analyserRef.current)

            const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)

            const updateAudioLevel = () => {
                if (analyserRef.current && isRecording) {
                    analyserRef.current.getByteFrequencyData(dataArray)
                    const average = dataArray.reduce((a, b) => a + b) / dataArray.length
                    setAudioLevel(average)
                    requestAnimationFrame(updateAudioLevel)
                }
            }

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0 && wsConnection) {
                    // Convert to base64 and send
                    const reader = new FileReader()
                    reader.onload = () => {
                        const base64Audio = (reader.result as string).split(',')[1]
                        wsConnection.send(JSON.stringify({
                            type: 'audio_message',
                            audio_data: base64Audio,
                            format: 'wav'
                        }))
                    }
                    reader.readAsDataURL(event.data)
                }
            }

            mediaRecorderRef.current.start()
            setIsRecording(true)
            updateAudioLevel()

            // Notify WebSocket
            if (wsConnection) {
                wsConnection.send(JSON.stringify({
                    type: 'voice_start'
                }))
            }

        } catch (error) {
            console.error('Error accessing microphone:', error)
        }
    }

    const stopVoiceRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop()
            setIsRecording(false)
            setAudioLevel(0)

            if (mediaRecorderRef.current.stream) {
                mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
            }

            // Notify WebSocket
            if (wsConnection) {
                wsConnection.send(JSON.stringify({
                    type: 'voice_stop'
                }))
            }
        }
    }

    const toggleRecording = () => {
        if (isRecording) {
            stopVoiceRecording()
        } else {
            startVoiceRecording()
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            sendMessage()
        }
    }

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setInputMessage(e.target.value)

        // Send typing indicators
        if (wsConnection) {
            if (!isTyping) {
                setIsTyping(true)
                wsConnection.send(JSON.stringify({ type: 'typing_start' }))
            }

            if (typingTimeoutRef.current) {
                clearTimeout(typingTimeoutRef.current)
            }

            typingTimeoutRef.current = setTimeout(() => {
                setIsTyping(false)
                wsConnection.send(JSON.stringify({ type: 'typing_stop' }))
            }, 1000)
        }
    }

    const updateTutorPersonality = (key: keyof TutorPersonality, value: any) => {
        const newPersonality = { ...tutorPersonality, [key]: value }
        setTutorPersonality(newPersonality)
        onPersonalityChange?.(newPersonality)
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b">
                <div className="flex items-center gap-3">
                    <Avatar className="w-10 h-10">
                        <AvatarImage src="/ai-tutor-avatar.png" />
                        <AvatarFallback>
                            <BrainCircuit className="w-5 h-5" />
                        </AvatarFallback>
                    </Avatar>
                    <div>
                        <h2 className="font-semibold">Enhanced AI Tutor</h2>
                        <p className="text-sm text-muted-foreground">Multi-modal learning assistant</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant={connectionStatus === 'connected' ? 'default' : 'secondary'} className="flex items-center gap-1">
                        <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500' :
                                connectionStatus === 'connecting' ? 'bg-yellow-500' : 'bg-red-500'
                            }`}></div>
                        {connectionStatus === 'connected' ? 'Connected' :
                            connectionStatus === 'connecting' ? 'Connecting' : 'Disconnected'}
                    </Badge>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex">
                {/* Chat Area */}
                <div className="flex-1 flex flex-col">
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="chat" className="flex items-center gap-2">
                                <MessageCircle className="w-4 h-4" />
                                Chat
                            </TabsTrigger>
                            <TabsTrigger value="voice" className="flex items-center gap-2">
                                <Headphones className="w-4 h-4" />
                                Voice
                            </TabsTrigger>
                            <TabsTrigger value="insights" className="flex items-center gap-2">
                                <BarChart3 className="w-4 h-4" />
                                Insights
                            </TabsTrigger>
                            <TabsTrigger value="settings" className="flex items-center gap-2">
                                <Settings className="w-4 h-4" />
                                Settings
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="chat" className="flex-1 flex flex-col">
                            <div className="flex-1 flex flex-col">
                                <ScrollArea className="flex-1 p-4">
                                    <div className="space-y-4">
                                        {messages.map((message) => (
                                            <div
                                                key={message.id}
                                                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                                            >
                                                <div className={`max-w-[80%] ${message.type === 'user' ? 'order-2' : 'order-1'}`}>
                                                    <div className={`rounded-lg p-3 ${message.type === 'user'
                                                            ? 'bg-primary text-primary-foreground'
                                                            : 'bg-muted'
                                                        }`}>
                                                        {message.content.text && (
                                                            <p className="text-sm">{message.content.text}</p>
                                                        )}

                                                        {message.content.exercise && (
                                                            <div className="mt-3 p-3 bg-background rounded border">
                                                                <h4 className="font-medium text-sm mb-2">{message.content.exercise.title}</h4>
                                                                <p className="text-xs text-muted-foreground mb-2">{message.content.exercise.description}</p>
                                                                <div className="flex items-center gap-2 text-xs">
                                                                    <Clock className="w-3 h-3" />
                                                                    {message.content.exercise.duration}s
                                                                </div>
                                                            </div>
                                                        )}

                                                        <div className="flex items-center gap-2 mt-2">
                                                            <p className="text-xs opacity-70">
                                                                {message.timestamp.toLocaleTimeString()}
                                                            </p>
                                                            <Badge variant="outline" className="text-xs">
                                                                {message.responseType}
                                                            </Badge>
                                                            <Badge variant="outline" className="text-xs">
                                                                {Math.round(message.confidence * 100)}%
                                                            </Badge>
                                                        </div>
                                                    </div>
                                                </div>
                                                <Avatar className={`w-8 h-8 ${message.type === 'user' ? 'order-1' : 'order-2'}`}>
                                                    <AvatarImage src={message.type === 'user' ? '/user-avatar.png' : '/ai-tutor-avatar.png'} />
                                                    <AvatarFallback>
                                                        {message.type === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                                                    </AvatarFallback>
                                                </Avatar>
                                            </div>
                                        ))}
                                        {isLoading && (
                                            <div className="flex justify-start">
                                                <div className="bg-muted rounded-lg p-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="flex space-x-1">
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                        </div>
                                                        <span className="text-xs text-muted-foreground">AI is thinking...</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                        {isTyping && (
                                            <div className="flex justify-start">
                                                <div className="bg-muted rounded-lg p-3">
                                                    <div className="flex items-center gap-2">
                                                        <div className="flex space-x-1">
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                            <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                                        </div>
                                                        <span className="text-xs text-muted-foreground">AI is typing...</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                        <div ref={messagesEndRef} />
                                    </div>
                                </ScrollArea>

                                <div className="p-4 border-t">
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
                                            onChange={handleInputChange}
                                            onKeyPress={handleKeyPress}
                                            placeholder="Type your message or use voice..."
                                            className="flex-1"
                                        />
                                        <Button onClick={sendMessage} disabled={!inputMessage.trim() || isLoading}>
                                            <Send className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </TabsContent>

                        <TabsContent value="voice" className="flex-1 p-4">
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Mic className="w-4 h-4" />
                                            Voice Interaction
                                        </CardTitle>
                                        <CardDescription>
                                            Practice speaking with real-time analysis and feedback
                                        </CardDescription>
                                    </CardHeader>
                                    <CardContent className="space-y-4">
                                        <div className="flex items-center justify-center h-32">
                                            <div className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${isRecording ? 'bg-red-500 text-white scale-110' : 'bg-muted'
                                                }`}>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="w-16 h-16"
                                                    onClick={toggleRecording}
                                                >
                                                    {isRecording ? <MicOff className="w-8 h-8" /> : <Mic className="w-8 h-8" />}
                                                </Button>
                                            </div>
                                        </div>

                                        {isRecording && (
                                            <div className="space-y-2">
                                                <div className="flex justify-between text-sm">
                                                    <span>Audio Level</span>
                                                    <span>{Math.round(audioLevel)}%</span>
                                                </div>
                                                <Progress value={audioLevel} className="w-full" />
                                            </div>
                                        )}

                                        <div className="text-center">
                                            <p className="text-sm text-muted-foreground">
                                                {isRecording ? 'Recording... Click to stop' : 'Click to start recording'}
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Volume2 className="w-4 h-4" />
                                            Audio Playback
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <audio ref={audioRef} controls className="w-full" />
                                        <div className="mt-4 space-y-2">
                                            <Button className="w-full" variant="outline">
                                                <PlayCircle className="w-4 h-4 mr-2" />
                                                Play Latest Response
                                            </Button>
                                            <Button className="w-full" variant="outline">
                                                <Volume2 className="w-4 h-4 mr-2" />
                                                Adjust Volume
                                            </Button>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </TabsContent>

                        <TabsContent value="insights" className="flex-1 p-4">
                            <div className="space-y-4">
                                {speechAnalysis && (
                                    <Card>
                                        <CardHeader>
                                            <CardTitle className="flex items-center gap-2">
                                                <BarChart3 className="w-4 h-4" />
                                                Speech Analysis
                                            </CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div>
                                                    <div className="flex justify-between text-sm mb-1">
                                                        <span>Pronunciation</span>
                                                        <span>{speechAnalysis.pronunciation}/10</span>
                                                    </div>
                                                    <Progress value={speechAnalysis.pronunciation * 10} className="w-full" />
                                                </div>
                                                <div>
                                                    <div className="flex justify-between text-sm mb-1">
                                                        <span>Fluency</span>
                                                        <span>{speechAnalysis.fluency}/10</span>
                                                    </div>
                                                    <Progress value={speechAnalysis.fluency * 10} className="w-full" />
                                                </div>
                                                <div>
                                                    <div className="flex justify-between text-sm mb-1">
                                                        <span>Grammar</span>
                                                        <span>{speechAnalysis.grammar}/10</span>
                                                    </div>
                                                    <Progress value={speechAnalysis.grammar * 10} className="w-full" />
                                                </div>
                                                <div>
                                                    <div className="flex justify-between text-sm mb-1">
                                                        <span>Vocabulary</span>
                                                        <span>{speechAnalysis.vocabulary}/10</span>
                                                    </div>
                                                    <Progress value={speechAnalysis.vocabulary * 10} className="w-full" />
                                                </div>
                                            </div>
                                        </CardContent>
                                    </Card>
                                )}

                                <Card>
                                    <CardHeader>
                                        <CardTitle className="flex items-center gap-2">
                                            <Target className="w-4 h-4" />
                                            Current Focus
                                        </CardTitle>
                                    </CardHeader>
                                    <CardContent>
                                        <div className="space-y-3">
                                            <div>
                                                <p className="text-sm font-medium">Teaching Style</p>
                                                <Badge variant="outline">{tutorPersonality.teachingStyle}</Badge>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium">Interaction Mode</p>
                                                <Badge variant="outline">{tutorPersonality.interactionMode}</Badge>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium">Difficulty Level</p>
                                                <Badge variant="outline">{tutorPersonality.difficultyLevel}</Badge>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        </TabsContent>

                        <TabsContent value="settings" className="flex-1 p-4">
                            <Card>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2">
                                        <Settings className="w-4 h-4" />
                                        Tutor Settings
                                    </CardTitle>
                                    <CardDescription>
                                        Customize your AI tutor experience
                                    </CardDescription>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-muted-foreground">Settings panel will be implemented here.</p>
                                </CardContent>
                            </Card>
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </div>
    )
}
