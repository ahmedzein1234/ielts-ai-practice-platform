'use client';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertCircle,
  CheckCircle,
  Clock,
  Info,
  Mic,
  MicOff,
  RotateCcw,
  Target,
  TrendingUp,
  Volume2
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { toast } from 'react-hot-toast';

interface SpeakingQuestion {
  id: string;
  type: 'part1' | 'part2' | 'part3';
  question: string;
  followUp?: string[];
  timeLimit: number;
  preparationTime?: number;
  bandTarget: number;
}

interface PronunciationScore {
  overall: number;
  individual_sounds: { [key: string]: number };
  stress_patterns: number;
  intonation: number;
  word_linking: number;
}

interface FluencyMetrics {
  speech_rate: number;
  pause_frequency: number;
  hesitation_ratio: number;
  smoothness: number;
}

interface AccentAnalysis {
  accent_type: string;
  comprehensibility: number;
  native_like_qualities: number;
  regional_features: string[];
}

interface SpeakingSession {
  id: string;
  questionId: string;
  audioUrl: string;
  transcript: string;
  score: number;
  feedback: string[];
  pronunciation: PronunciationScore;
  fluency: FluencyMetrics;
  accent: AccentAnalysis;
  overall_score: number;
  band_level: string;
  recommendations: string[];
  practice_suggestions: string[];
  timestamp: Date;
  duration: number;
}

const mockQuestions: SpeakingQuestion[] = [
  {
    id: '1',
    type: 'part1',
    question: 'Tell me about your hometown.',
    followUp: ['What do you like most about it?', 'How has it changed over the years?'],
    timeLimit: 120,
    bandTarget: 7.0
  },
  {
    id: '2',
    type: 'part2',
    question: 'Describe a place you would like to visit. You should say:\n- where this place is\n- how you know about this place\n- what you would do there\n- and explain why you would like to visit this place.',
    timeLimit: 180,
    preparationTime: 60,
    bandTarget: 7.0
  },
  {
    id: '3',
    type: 'part3',
    question: 'Let\'s talk about travel and tourism.',
    followUp: [
      'What are the benefits of travelling?',
      'How has tourism changed in recent years?',
      'What impact does tourism have on local communities?'
    ],
    timeLimit: 240,
    bandTarget: 7.0
  }
];

export default function SpeakingPage() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState<SpeakingQuestion | null>(null);
  const [session, setSession] = useState<SpeakingSession | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [preparationTime, setPreparationTime] = useState(0);
  const [isInPreparation, setIsInPreparation] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);
  const [sessions, setSessions] = useState<SpeakingSession[]>([]);
  const [selectedTab, setSelectedTab] = useState('practice');
  const [error, setError] = useState<string | null>(null);

  const audioRef = useRef<HTMLAudioElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const prepTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Load previous sessions from localStorage
    const savedSessions = localStorage.getItem('speaking_sessions');
    if (savedSessions) {
      setSessions(JSON.parse(savedSessions));
    }
  }, []);

  useEffect(() => {
    if (isRecording) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording]);

  useEffect(() => {
    if (isInPreparation) {
      prepTimerRef.current = setInterval(() => {
        setPreparationTime(prev => {
          if (prev >= (currentQuestion?.preparationTime || 0)) {
            setIsInPreparation(false);
            startRecording();
            return 0;
          }
          return prev + 1;
        });
      }, 1000);
    } else {
      if (prepTimerRef.current) {
        clearInterval(prepTimerRef.current);
      }
    }

    return () => {
      if (prepTimerRef.current) {
        clearInterval(prepTimerRef.current);
      }
    };
  }, [isInPreparation, currentQuestion]);

  const startPreparation = async (question: SpeakingQuestion) => {
    setCurrentQuestion(question);
    setSession(null);
    setShowFeedback(false);
    setError(null);
    setRecordingTime(0);
    setPreparationTime(0);

    if (question.preparationTime) {
      setIsInPreparation(true);
      toast.success(`Preparation time started. You have ${question.preparationTime} seconds.`);
    } else {
      startRecording();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      recorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        processRecording(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      setMediaRecorder(recorder);
      setAudioChunks(chunks);
      recorder.start();
      setIsRecording(true);
      toast.success('Recording started!');
    } catch (error) {
      console.error('Error accessing microphone:', error);
      setError('Unable to access microphone. Please check permissions.');
      toast.error('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      toast.success('Recording stopped. Processing...');
    }
  };

  const processRecording = async (audioBlob: Blob) => {
    setIsProcessing(true);
    try {
              const arrayBuffer = await audioBlob.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        const base64Audio = btoa(String.fromCharCode.apply(null, Array.from(uint8Array)));
      
      const response = await fetch('http://localhost:8003/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_data: base64Audio,
          sample_rate: 16000,
          language: 'en',
          include_pronunciation: true,
          include_fluency: true,
          include_accent: true,
          target_band: currentQuestion?.bandTarget || 7.0
        }),
      });

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }

      const analysisResult = await response.json();
      
      const newSession: SpeakingSession = {
        id: `session_${Date.now()}`,
        questionId: currentQuestion?.id || '',
        audioUrl: URL.createObjectURL(audioBlob),
        transcript: analysisResult.transcription?.text || 'No transcript available',
        score: analysisResult.overall_score || 0,
        feedback: analysisResult.recommendations || [],
        pronunciation: analysisResult.pronunciation || {
          overall: 0,
          individual_sounds: {},
          stress_patterns: 0,
          intonation: 0,
          word_linking: 0
        },
        fluency: analysisResult.fluency || {
          speech_rate: 0,
          pause_frequency: 0,
          hesitation_ratio: 0,
          smoothness: 0
        },
        accent: analysisResult.accent || {
          accent_type: 'Unknown',
          comprehensibility: 0,
          native_like_qualities: 0,
          regional_features: []
        },
        overall_score: analysisResult.overall_score || 0,
        band_level: analysisResult.band_level || 'Unknown',
        recommendations: analysisResult.recommendations || [],
        practice_suggestions: analysisResult.practice_suggestions || [],
        timestamp: new Date(),
        duration: recordingTime
      };

      setSession(newSession);
      setShowFeedback(true);
      
      // Save to sessions history
      const updatedSessions = [newSession, ...sessions];
      setSessions(updatedSessions);
      localStorage.setItem('speaking_sessions', JSON.stringify(updatedSessions));
      
      toast.success('Analysis complete! Check your detailed feedback.');
    } catch (error) {
      console.error('Processing error:', error);
      setError('Failed to process recording. Please try again.');
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

  const getBandColor = (band: string) => {
    const bandNum = parseFloat(band);
    if (bandNum >= 8.0) return 'bg-green-500';
    if (bandNum >= 7.0) return 'bg-blue-500';
    if (bandNum >= 6.0) return 'bg-yellow-500';
    if (bandNum >= 5.0) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreColor = (score: number) => {
    if (score >= 8.0) return 'text-green-600';
    if (score >= 7.0) return 'text-blue-600';
    if (score >= 6.0) return 'text-yellow-600';
    if (score >= 5.0) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Speaking Practice</h1>
          <p className="text-muted-foreground">
            Practice your IELTS speaking skills with AI-powered feedback
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          <Target className="w-4 h-4 mr-1" />
          Target: Band 7.0+
        </Badge>
      </div>

      <Tabs value={selectedTab} onValueChange={setSelectedTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="practice">Practice</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="practice" className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {!currentQuestion && (
            <Card>
              <CardHeader>
                <CardTitle>Choose a Question</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {mockQuestions.map((question) => (
                  <Card key={question.id} className="cursor-pointer hover:bg-muted/50 transition-colors">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <Badge variant={question.type === 'part1' ? 'default' : question.type === 'part2' ? 'secondary' : 'outline'}>
                              Part {question.type.slice(-1)}
                            </Badge>
                            <Badge variant="outline">
                              <Clock className="w-3 h-3 mr-1" />
                              {formatTime(question.timeLimit)}
                            </Badge>
                            {question.preparationTime && (
                              <Badge variant="outline">
                                <Info className="w-3 h-3 mr-1" />
                                Prep: {formatTime(question.preparationTime)}
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm whitespace-pre-line">{question.question}</p>
                          {question.followUp && (
                            <div className="mt-2">
                              <p className="text-xs text-muted-foreground">Follow-up questions:</p>
                              <ul className="text-xs text-muted-foreground list-disc list-inside">
                                {question.followUp.map((q, idx) => (
                                  <li key={idx}>{q}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                        <Button 
                          onClick={() => startPreparation(question)}
                          disabled={isRecording || isProcessing}
                          size="sm"
                        >
                          Start
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </CardContent>
            </Card>
          )}

          {currentQuestion && !showFeedback && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {isInPreparation ? (
                    <>
                      <Clock className="w-5 h-5" />
                      Preparation Time
                    </>
                  ) : (
                    <>
                      <Mic className="w-5 h-5" />
                      Recording
                    </>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>Question:</span>
                    <Badge variant="outline">Part {currentQuestion.type.slice(-1)}</Badge>
                  </div>
                  <p className="text-sm bg-muted p-3 rounded-md whitespace-pre-line">
                    {currentQuestion.question}
                  </p>
                </div>

                {isInPreparation && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Preparation Time Remaining:</span>
                      <span className="font-mono">
                        {formatTime((currentQuestion.preparationTime || 0) - preparationTime)}
                      </span>
                    </div>
                    <Progress 
                      value={((currentQuestion.preparationTime || 0) - preparationTime) / (currentQuestion.preparationTime || 1) * 100} 
                      className="h-2"
                    />
                  </div>
                )}

                {isRecording && (
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Recording Time:</span>
                      <span className="font-mono">{formatTime(recordingTime)}</span>
                    </div>
                    <Progress 
                      value={(recordingTime / currentQuestion.timeLimit) * 100} 
                      className="h-2"
                    />
                  </div>
                )}

                <div className="flex gap-2">
                  {!isRecording && !isInPreparation && (
                    <Button onClick={startRecording} disabled={isProcessing}>
                      <Mic className="w-4 h-4 mr-2" />
                      Start Recording
                    </Button>
                  )}
                  {isRecording && (
                    <Button onClick={stopRecording} variant="destructive">
                      <MicOff className="w-4 h-4 mr-2" />
                      Stop Recording
                    </Button>
                  )}
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setCurrentQuestion(null);
                      setSession(null);
                      setShowFeedback(false);
                      setError(null);
                      setRecordingTime(0);
                      setPreparationTime(0);
                      setIsInPreparation(false);
                    }}
                  >
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                </div>

                {isProcessing && (
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      Processing your recording... This may take a few moments.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="feedback" className="space-y-6">
          {session && showFeedback ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Analysis Results
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold mb-1">
                        <span className={getScoreColor(session.overall_score)}>
                          {session.overall_score.toFixed(1)}
                        </span>
                      </div>
                      <div className="text-sm text-muted-foreground">Overall Score</div>
                    </div>
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <Badge className={`${getBandColor(session.band_level)} text-white`}>
                        Band {session.band_level}
                      </Badge>
                      <div className="text-sm text-muted-foreground mt-1">Band Level</div>
                    </div>
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold mb-1">{formatTime(session.duration)}</div>
                      <div className="text-sm text-muted-foreground">Duration</div>
                    </div>
                  </div>

                  {session.audioUrl && (
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Your Recording:</label>
                      <audio ref={audioRef} controls className="w-full">
                        <source src={session.audioUrl} type="audio/wav" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}

                  <div className="space-y-2">
                    <label className="text-sm font-medium">Transcript:</label>
                    <div className="bg-muted p-3 rounded-md text-sm">
                      {session.transcript || 'No transcript available'}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Volume2 className="w-5 h-5" />
                      Pronunciation Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Overall Pronunciation</span>
                        <span className={getScoreColor(session.pronunciation.overall)}>
                          {session.pronunciation.overall.toFixed(1)}/10
                        </span>
                      </div>
                      <Progress value={session.pronunciation.overall * 10} className="h-2" />
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Stress Patterns</span>
                        <span>{session.pronunciation.stress_patterns.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.pronunciation.stress_patterns * 10} className="h-2" />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Intonation</span>
                        <span>{session.pronunciation.intonation.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.pronunciation.intonation * 10} className="h-2" />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Word Linking</span>
                        <span>{session.pronunciation.word_linking.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.pronunciation.word_linking * 10} className="h-2" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Fluency Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Speech Rate</span>
                        <span>{session.fluency.speech_rate.toFixed(1)} words/min</span>
                      </div>
                      <Progress value={Math.min(session.fluency.speech_rate / 150 * 100, 100)} className="h-2" />
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Smoothness</span>
                        <span>{session.fluency.smoothness.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.fluency.smoothness * 10} className="h-2" />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Pause Frequency</span>
                        <span>{session.fluency.pause_frequency.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.fluency.pause_frequency * 10} className="h-2" />
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Hesitation Ratio</span>
                        <span>{session.fluency.hesitation_ratio.toFixed(1)}/10</span>
                      </div>
                      <Progress value={session.fluency.hesitation_ratio * 10} className="h-2" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Recommendations & Practice Suggestions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {session.recommendations.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Key Recommendations:</h4>
                      <ul className="space-y-1">
                        {session.recommendations.map((rec, idx) => (
                          <li key={idx} className="text-sm flex items-start gap-2">
                            <CheckCircle className="w-4 h-4 mt-0.5 text-green-600" />
                            {rec}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {session.practice_suggestions.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2">Practice Suggestions:</h4>
                      <ul className="space-y-1">
                        {session.practice_suggestions.map((suggestion, idx) => (
                          <li key={idx} className="text-sm flex items-start gap-2">
                            <Target className="w-4 h-4 mt-0.5 text-blue-600" />
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Info className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">No Feedback Available</h3>
                <p className="text-muted-foreground">
                  Complete a speaking practice session to see detailed feedback and analysis.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          {sessions.length > 0 ? (
            <div className="space-y-4">
              {sessions.map((session) => (
                <Card key={session.id} className="cursor-pointer hover:bg-muted/50 transition-colors">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className={`${getBandColor(session.band_level)} text-white`}>
                            Band {session.band_level}
                          </Badge>
                          <Badge variant="outline">
                            Score: {session.overall_score.toFixed(1)}
                          </Badge>
                          <Badge variant="outline">
                            <Clock className="w-3 h-3 mr-1" />
                            {formatTime(session.duration)}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {session.timestamp.toLocaleDateString()} at {session.timestamp.toLocaleTimeString()}
                        </p>
                        <p className="text-sm mt-1 line-clamp-2">
                          {session.transcript}
                        </p>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSession(session);
                          setShowFeedback(true);
                          setSelectedTab('feedback');
                        }}
                      >
                        View Details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Clock className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">No Practice History</h3>
                <p className="text-muted-foreground">
                  Your speaking practice sessions will appear here.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
