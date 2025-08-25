'use client';

import { useAuth } from '@/components/providers/auth-provider';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import {
  Loader2,
  Mic,
  MicOff,
  Pause,
  Play,
  RotateCcw,
  Settings,
  Target,
  Timer,
  Volume2,
  VolumeX
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import toast from 'react-hot-toast';

interface SpeakingQuestion {
  id: string;
  part: 1 | 2 | 3;
  title: string;
  prompt: string;
  preparationTime?: number;
  speakingTime?: number;
  followUpQuestions?: string[];
}

interface SpeakingSession {
  id: string;
  question: SpeakingQuestion;
  transcript: string;
  duration: number;
  score?: number;
  feedback?: {
    fluency: number;
    pronunciation: number;
    vocabulary: number;
    grammar: number;
    coherence: number;
  };
  recordingUrl?: string;
}

const mockQuestions: SpeakingQuestion[] = [
  {
    id: '1',
    part: 1,
    title: 'Personal Information',
    prompt: 'Tell me about your hometown.',
    preparationTime: 0,
    speakingTime: 60,
  },
  {
    id: '2',
    part: 2,
    title: 'Describe a memorable journey',
    prompt: 'Describe a journey you remember well. You should say:\n• Where you went\n• When you went there\n• Who you went with\n• And explain why you remember this journey well.',
    preparationTime: 60,
    speakingTime: 120,
  },
  {
    id: '3',
    part: 3,
    title: 'Travel and Tourism',
    prompt: 'Let\'s talk about travel and tourism. What are the benefits of traveling to different countries?',
    preparationTime: 0,
    speakingTime: 90,
    followUpQuestions: [
      'How has tourism changed in recent years?',
      'What impact does tourism have on local communities?',
      'Do you think people should travel more or less?',
    ],
  },
];

export default function SpeakingPage() {
  const { user } = useAuth();
  const [currentQuestion, setCurrentQuestion] = useState<SpeakingQuestion | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [session, setSession] = useState<SpeakingSession | null>(null);
  const [preparationTime, setPreparationTime] = useState(0);
  const [speakingTime, setSpeakingTime] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [isMuted, setIsMuted] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const socketRef = useRef<WebSocket | null>(null);
  const preparationTimerRef = useRef<NodeJS.Timeout | null>(null);
  const speakingTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Initialize WebSocket connection for real-time transcription
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8002/ws/speech');

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'transcript') {
          setTranscript(data.text);
        } else if (data.type === 'final_transcript') {
          setTranscript(data.text);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        toast.error('Connection error. Please try again.');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };

      socketRef.current = ws;
    };

    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  const startPreparation = (question: SpeakingQuestion) => {
    setCurrentQuestion(question);
    setTranscript('');
    setSession(null);
    setShowFeedback(false);

    if (question.preparationTime && question.preparationTime > 0) {
      setPreparationTime(question.preparationTime);
      preparationTimerRef.current = setInterval(() => {
        setPreparationTime((prev) => {
          if (prev <= 1) {
            clearInterval(preparationTimerRef.current!);
            startSpeaking();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      startSpeaking();
    }
  };

  const startSpeaking = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await processRecording(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setSpeakingTime(currentQuestion?.speakingTime || 120);

      speakingTimerRef.current = setInterval(() => {
        setSpeakingTime((prev) => {
          if (prev <= 1) {
            stopRecording();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error('Unable to access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
      setIsPaused(false);
    }

    if (speakingTimerRef.current) {
      clearInterval(speakingTimerRef.current);
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.pause();
      setIsPaused(true);
    }
  };

  const resumeRecording = () => {
    if (mediaRecorderRef.current && isPaused) {
      mediaRecorderRef.current.resume();
      setIsPaused(false);
    }
  };

  const processRecording = async (audioBlob: Blob) => {
    setIsProcessing(true);

    try {
      // Convert audio to base64
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const base64Audio = btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));

      // Send to scoring service
      const response = await fetch('/api/speaking/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          question_id: currentQuestion?.id,
          transcript: transcript,
          audio_data: base64Audio,
          duration: currentQuestion?.speakingTime || 120,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const newSession: SpeakingSession = {
          id: result.session_id,
          question: currentQuestion!,
          transcript: transcript,
          duration: currentQuestion?.speakingTime || 120,
          score: result.score,
          feedback: result.feedback,
          recordingUrl: result.recording_url,
        };
        setSession(newSession);
        setShowFeedback(true);
        toast.success('Speaking session completed!');
      } else {
        throw new Error('Failed to process recording');
      }
    } catch (error) {
      console.error('Error processing recording:', error);
      toast.error('Failed to process recording. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getBandScoreClass = (score: number) => {
    if (score >= 7.5) return 'band-score-7-8';
    if (score >= 6.5) return 'band-score-5-6';
    if (score >= 5.5) return 'band-score-3-4';
    return 'band-score-1-2';
  };

  const resetSession = () => {
    setCurrentQuestion(null);
    setTranscript('');
    setSession(null);
    setShowFeedback(false);
    setPreparationTime(0);
    setSpeakingTime(0);
    setIsRecording(false);
    setIsPaused(false);
    setIsProcessing(false);

    if (preparationTimerRef.current) {
      clearInterval(preparationTimerRef.current);
    }
    if (speakingTimerRef.current) {
      clearInterval(speakingTimerRef.current);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Speaking Practice</h1>
          <p className="text-muted-foreground">
            Practice your speaking skills with AI-powered feedback
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Settings className="mr-2 h-4 w-4" />
          Settings
        </Button>
      </div>

      {!currentQuestion && !showFeedback && (
        /* Question Selection */
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {mockQuestions.map((question) => (
            <Card key={question.id} className="hover:shadow-lg transition-all duration-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <Badge variant="secondary">Part {question.part}</Badge>
                  <div className="flex items-center space-x-2">
                    {question.preparationTime && question.preparationTime > 0 && (
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Timer className="mr-1 h-4 w-4" />
                        {formatTime(question.preparationTime)}
                      </div>
                    )}
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Target className="mr-1 h-4 w-4" />
                      {formatTime(question.speakingTime || 120)}
                    </div>
                  </div>
                </div>
                <CardTitle className="text-lg">{question.title}</CardTitle>
                <CardDescription className="text-sm">
                  {question.prompt.length > 100
                    ? `${question.prompt.substring(0, 100)}...`
                    : question.prompt}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => startPreparation(question)}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  <Mic className="mr-2 h-4 w-4" />
                  Start Practice
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {currentQuestion && !showFeedback && (
        /* Speaking Session */
        <div className="space-y-6">
          {/* Question Display */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Part {currentQuestion.part}</Badge>
                  <CardTitle>{currentQuestion.title}</CardTitle>
                </div>
                <div className="flex items-center space-x-4">
                  {preparationTime > 0 && (
                    <div className="flex items-center space-x-2">
                      <Timer className="h-4 w-4 text-orange-600" />
                      <span className="text-sm font-medium">
                        Preparation: {formatTime(preparationTime)}
                      </span>
                    </div>
                  )}
                  {speakingTime > 0 && (
                    <div className="flex items-center space-x-2">
                      <Target className="h-4 w-4 text-blue-600" />
                      <span className="text-sm font-medium">
                        Speaking: {formatTime(speakingTime)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none">
                <p className="whitespace-pre-line">{currentQuestion.prompt}</p>
              </div>
            </CardContent>
          </Card>

          {/* Recording Interface */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Mic className="h-5 w-5" />
                <span>Recording</span>
                {isRecording && (
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="text-sm text-muted-foreground">Live</span>
                  </div>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Controls */}
              <div className="flex items-center justify-center space-x-4">
                {!isRecording && preparationTime === 0 && (
                  <Button
                    onClick={startSpeaking}
                    size="lg"
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Mic className="mr-2 h-5 w-5" />
                    Start Recording
                  </Button>
                )}

                {isRecording && !isPaused && (
                  <Button
                    onClick={pauseRecording}
                    variant="outline"
                    size="lg"
                  >
                    <Pause className="mr-2 h-5 w-5" />
                    Pause
                  </Button>
                )}

                {isRecording && isPaused && (
                  <Button
                    onClick={resumeRecording}
                    variant="outline"
                    size="lg"
                  >
                    <Play className="mr-2 h-5 w-5" />
                    Resume
                  </Button>
                )}

                {isRecording && (
                  <Button
                    onClick={stopRecording}
                    variant="destructive"
                    size="lg"
                  >
                    <MicOff className="mr-2 h-5 w-5" />
                    Stop
                  </Button>
                )}

                <Button
                  onClick={resetSession}
                  variant="ghost"
                  size="lg"
                >
                  <RotateCcw className="mr-2 h-5 w-5" />
                  Reset
                </Button>
              </div>

              {/* Transcript */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium">Live Transcript</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsMuted(!isMuted)}
                  >
                    {isMuted ? (
                      <VolumeX className="h-4 w-4" />
                    ) : (
                      <Volume2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <div className="min-h-[100px] p-4 border rounded-lg bg-muted/50">
                  {transcript ? (
                    <p className="text-sm leading-relaxed">{transcript}</p>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {isRecording ? 'Listening...' : 'Start recording to see your transcript'}
                    </p>
                  )}
                </div>
              </div>

              {/* Processing State */}
              {isProcessing && (
                <Alert>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <AlertDescription>
                    Processing your recording and generating feedback...
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {showFeedback && session && (
        /* Feedback Display */
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Speaking Feedback</span>
                {session.score && (
                  <Badge className={getBandScoreClass(session.score)}>
                    Band {session.score.toFixed(1)}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Score Breakdown */}
              {session.feedback && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
                  {Object.entries(session.feedback).map(([criterion, score]) => (
                    <div key={criterion} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">
                          {criterion}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {score.toFixed(1)}
                        </span>
                      </div>
                      <Progress value={(score / 9) * 100} className="h-2" />
                    </div>
                  ))}
                </div>
              )}

              {/* Transcript */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Your Response</h4>
                <div className="p-4 border rounded-lg bg-muted/50">
                  <p className="text-sm leading-relaxed">{session.transcript}</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-4">
                <Button
                  onClick={resetSession}
                  variant="outline"
                >
                  <RotateCcw className="mr-2 h-4 w-4" />
                  Practice Again
                </Button>
                <Button
                  onClick={() => setShowFeedback(false)}
                  variant="outline"
                >
                  Try Different Question
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
