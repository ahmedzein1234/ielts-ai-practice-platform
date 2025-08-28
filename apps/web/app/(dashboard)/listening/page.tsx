'use client';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useEffect, useRef, useState } from 'react';
// RadioGroup component not available, using custom implementation
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
    AlertCircle,
    BookOpen,
    CheckCircle,
    Clock,
    Headphones,
    Info,
    Pause,
    Play,
    RotateCcw,
    Target,
    Timer
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ListeningQuestion {
  id: string;
  type: 'multiple_choice' | 'fill_blank' | 'matching' | 'true_false' | 'short_answer';
  question: string;
  options?: string[];
  correctAnswer: string | string[];
  audioUrl?: string;
  transcript?: string;
  timeLimit: number;
  bandTarget: number;
  section: 'section1' | 'section2' | 'section3' | 'section4';
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}

interface ListeningSession {
  id: string;
  questionId: string;
  userAnswer: string | string[];
  isCorrect: boolean;
  score: number;
  timeTaken: number;
  timestamp: Date;
  feedback: string[];
  bandLevel: string;
  overallScore: number;
}

const mockQuestions: ListeningQuestion[] = [
  {
    id: '1',
    type: 'multiple_choice',
    question: 'What is the main topic of the conversation?',
    options: [
      'University accommodation',
      'Student registration',
      'Library services',
      'Campus facilities'
    ],
    correctAnswer: 'University accommodation',
    audioUrl: '/audio/listening-1.mp3',
    transcript: 'Student: Hi, I\'m looking for information about accommodation on campus. Staff: Of course, let me help you with that. We have several options available...',
    timeLimit: 60,
    bandTarget: 6.0,
    section: 'section1',
    difficulty: 'intermediate'
  },
  {
    id: '2',
    type: 'fill_blank',
    question: 'Complete the sentence: The library is open from _____ to _____ on weekdays.',
    correctAnswer: ['9:00 AM', '8:00 PM'],
    audioUrl: '/audio/listening-2.mp3',
    transcript: 'The library opening hours are from 9:00 AM to 8:00 PM on weekdays, and from 10:00 AM to 6:00 PM on weekends.',
    timeLimit: 45,
    bandTarget: 6.5,
    section: 'section1',
    difficulty: 'intermediate'
  },
  {
    id: '3',
    type: 'true_false',
    question: 'The speaker mentions that online registration is mandatory for all students.',
    correctAnswer: 'false',
    audioUrl: '/audio/listening-3.mp3',
    transcript: 'While we encourage online registration for convenience, it\'s not mandatory. Students can still register in person if they prefer.',
    timeLimit: 30,
    bandTarget: 7.0,
    section: 'section2',
    difficulty: 'advanced'
  },
  {
    id: '4',
    type: 'matching',
    question: 'Match the facilities with their locations:',
    options: [
      'Computer Lab',
      'Cafeteria',
      'Gym',
      'Bookstore'
    ],
    correctAnswer: ['Building A', 'Building B', 'Building C', 'Building D'],
    audioUrl: '/audio/listening-4.mp3',
    transcript: 'The computer lab is located in Building A, the cafeteria in Building B, the gym in Building C, and the bookstore in Building D.',
    timeLimit: 90,
    bandTarget: 7.5,
    section: 'section3',
    difficulty: 'advanced'
  },
  {
    id: '5',
    type: 'short_answer',
    question: 'What is the maximum number of books a student can borrow at once?',
    correctAnswer: '10',
    audioUrl: '/audio/listening-5.mp3',
    transcript: 'Students can borrow up to 10 books at a time, with a loan period of 3 weeks.',
    timeLimit: 40,
    bandTarget: 6.0,
    section: 'section1',
    difficulty: 'intermediate'
  }
];

export default function ListeningPage() {
  const [currentQuestion, setCurrentQuestion] = useState<ListeningQuestion | null>(null);
  const [userAnswer, setUserAnswer] = useState<string | string[]>('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [session, setSession] = useState<ListeningSession | null>(null);
  const [sessions, setSessions] = useState<ListeningSession[]>([]);
  const [selectedTab, setSelectedTab] = useState('practice');
  const [error, setError] = useState<string | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Load previous sessions from localStorage
    const savedSessions = localStorage.getItem('listening_sessions');
    if (savedSessions) {
      setSessions(JSON.parse(savedSessions));
    }
  }, []);

  useEffect(() => {
    if (timeRemaining > 0 && !isSubmitted) {
      timerRef.current = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
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
  }, [timeRemaining, isSubmitted]);

  const startQuestion = (question: ListeningQuestion) => {
    setCurrentQuestion(question);
    setUserAnswer('');
    setIsSubmitted(false);
    setSession(null);
    setError(null);
    setTimeRemaining(question.timeLimit);
    setShowTranscript(false);
    setIsPlaying(false);
    
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  };

  const togglePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleSubmit = () => {
    if (!currentQuestion) return;

    setIsSubmitted(true);
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    // Calculate score and feedback
    const isCorrect = checkAnswer(userAnswer, currentQuestion.correctAnswer);
    const score = isCorrect ? 100 : 0;
    const bandLevel = getBandLevel(score);
    const overallScore = score;

    const newSession: ListeningSession = {
      id: `session_${Date.now()}`,
      questionId: currentQuestion.id,
      userAnswer: userAnswer,
      isCorrect: isCorrect,
      score: score,
      timeTaken: currentQuestion.timeLimit - timeRemaining,
      timestamp: new Date(),
      feedback: generateFeedback(userAnswer, currentQuestion),
      bandLevel: bandLevel,
      overallScore: overallScore
    };

    setSession(newSession);
    
    // Save to sessions history
    const updatedSessions = [newSession, ...sessions];
    setSessions(updatedSessions);
    localStorage.setItem('listening_sessions', JSON.stringify(updatedSessions));

    toast.success(isCorrect ? 'Correct answer!' : 'Incorrect answer. Check the feedback.');
  };

  const checkAnswer = (userAnswer: string | string[], correctAnswer: string | string[]): boolean => {
    if (Array.isArray(correctAnswer)) {
      if (Array.isArray(userAnswer)) {
        return userAnswer.length === correctAnswer.length && 
               userAnswer.every((ans, idx) => ans.toLowerCase().trim() === correctAnswer[idx].toLowerCase().trim());
      }
      return false;
    } else {
      return userAnswer.toString().toLowerCase().trim() === correctAnswer.toLowerCase().trim();
    }
  };

  const getBandLevel = (score: number): string => {
    if (score >= 90) return '8.0';
    if (score >= 80) return '7.5';
    if (score >= 70) return '7.0';
    if (score >= 60) return '6.5';
    if (score >= 50) return '6.0';
    if (score >= 40) return '5.5';
    if (score >= 30) return '5.0';
    return '4.5';
  };

  const generateFeedback = (userAnswer: string | string[], question: ListeningQuestion): string[] => {
    const feedback: string[] = [];
    
    if (checkAnswer(userAnswer, question.correctAnswer)) {
      feedback.push('Excellent! You answered correctly.');
      feedback.push('You demonstrated good listening comprehension.');
    } else {
      feedback.push('Incorrect answer. The correct answer was: ' + (Array.isArray(question.correctAnswer) ? question.correctAnswer.join(', ') : question.correctAnswer));
      feedback.push('Try listening to the audio again and pay attention to key details.');
      feedback.push('Consider taking notes while listening to help with comprehension.');
    }

    return feedback;
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

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-blue-100 text-blue-800';
      case 'advanced': return 'bg-yellow-100 text-yellow-800';
      case 'expert': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderQuestionInput = () => {
    if (!currentQuestion) return null;

    switch (currentQuestion.type) {
      case 'multiple_choice':
        return (
          <div className="space-y-2">
            {currentQuestion.options?.map((option, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <input
                  type="radio"
                  id={`option-${idx}`}
                  name="multiple-choice"
                  value={option}
                  checked={userAnswer === option}
                  onChange={(e) => setUserAnswer(e.target.value)}
                  className="w-4 h-4"
                />
                <Label htmlFor={`option-${idx}`}>{option}</Label>
              </div>
            ))}
          </div>
        );

      case 'fill_blank':
        return (
          <div className="space-y-2">
            {Array.isArray(currentQuestion.correctAnswer) ? (
              currentQuestion.correctAnswer.map((_, idx) => (
                <Input
                  key={idx}
                  placeholder={`Answer ${idx + 1}`}
                  value={Array.isArray(userAnswer) ? userAnswer[idx] || '' : ''}
                  onChange={(e) => {
                    const newAnswers = Array.isArray(userAnswer) ? [...userAnswer] : [];
                    newAnswers[idx] = e.target.value;
                    setUserAnswer(newAnswers);
                  }}
                />
              ))
            ) : (
              <Input
                placeholder="Enter your answer"
                value={userAnswer as string}
                onChange={(e) => setUserAnswer(e.target.value)}
              />
            )}
          </div>
        );

      case 'true_false':
        return (
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="true"
                name="true-false"
                value="true"
                checked={userAnswer === 'true'}
                onChange={(e) => setUserAnswer(e.target.value)}
                className="w-4 h-4"
              />
              <Label htmlFor="true">True</Label>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="radio"
                id="false"
                name="true-false"
                value="false"
                checked={userAnswer === 'false'}
                onChange={(e) => setUserAnswer(e.target.value)}
                className="w-4 h-4"
              />
              <Label htmlFor="false">False</Label>
            </div>
          </div>
        );

      case 'matching':
        return (
          <div className="space-y-4">
            {currentQuestion.options?.map((option, idx) => (
              <div key={idx} className="flex items-center space-x-2">
                <span className="text-sm font-medium">{option}:</span>
                <Input
                  placeholder="Match with..."
                  value={Array.isArray(userAnswer) ? userAnswer[idx] || '' : ''}
                  onChange={(e) => {
                    const newAnswers = Array.isArray(userAnswer) ? [...userAnswer] : [];
                    newAnswers[idx] = e.target.value;
                    setUserAnswer(newAnswers);
                  }}
                />
              </div>
            ))}
          </div>
        );

      case 'short_answer':
        return (
          <Input
            placeholder="Enter your answer"
            value={userAnswer as string}
            onChange={(e) => setUserAnswer(e.target.value)}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Listening Practice</h1>
          <p className="text-muted-foreground">
            Practice your IELTS listening skills with various question types
          </p>
        </div>
        <Badge variant="outline" className="text-sm">
          <Headphones className="w-4 h-4 mr-1" />
          Target: Band 6.0+
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
                            <Badge variant="outline">
                              {question.section.replace('section', 'Section ')}
                            </Badge>
                            <Badge className={getDifficultyColor(question.difficulty)}>
                              {question.difficulty}
                            </Badge>
                            <Badge variant="outline">
                              <Clock className="w-3 h-3 mr-1" />
                              {formatTime(question.timeLimit)}
                            </Badge>
                            <Badge variant="outline">
                              <Target className="w-3 h-3 mr-1" />
                              Band {question.bandTarget}
                            </Badge>
                          </div>
                          <p className="text-sm mb-2">{question.question}</p>
                          <p className="text-xs text-muted-foreground">
                            Type: {question.type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </p>
                        </div>
                        <Button 
                          onClick={() => startQuestion(question)}
                          disabled={isPlaying}
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

          {currentQuestion && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Headphones className="w-5 h-5" />
                  Listening Practice
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">
                        {currentQuestion.section.replace('section', 'Section ')}
                      </Badge>
                      <Badge className={getDifficultyColor(currentQuestion.difficulty)}>
                        {currentQuestion.difficulty}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Timer className="w-4 h-4" />
                      <span className="font-mono">{formatTime(timeRemaining)}</span>
                    </div>
                  </div>

                  <Progress 
                    value={((currentQuestion.timeLimit - timeRemaining) / currentQuestion.timeLimit) * 100} 
                    className="h-2"
                  />

                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Button onClick={togglePlayPause} disabled={!currentQuestion.audioUrl}>
                        {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        {isPlaying ? 'Pause' : 'Play'}
                      </Button>
                      {currentQuestion.transcript && (
                        <Button 
                          variant="outline" 
                          onClick={() => setShowTranscript(!showTranscript)}
                        >
                          <BookOpen className="w-4 h-4 mr-2" />
                          {showTranscript ? 'Hide' : 'Show'} Transcript
                        </Button>
                      )}
                    </div>

                    {currentQuestion.audioUrl && (
                      <audio
                        ref={audioRef}
                        src={currentQuestion.audioUrl}
                        onEnded={handleAudioEnded}
                        className="w-full"
                      />
                    )}

                    {showTranscript && currentQuestion.transcript && (
                      <div className="bg-muted p-3 rounded-md">
                        <p className="text-sm">{currentQuestion.transcript}</p>
                      </div>
                    )}
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <h3 className="font-medium">Question:</h3>
                    <p className="text-sm">{currentQuestion.question}</p>
                    
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Your Answer:</label>
                      {renderQuestionInput()}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      onClick={handleSubmit}
                      disabled={isSubmitted || !userAnswer}
                    >
                      Submit Answer
                    </Button>
                    <Button 
                      variant="outline" 
                      onClick={() => {
                        setCurrentQuestion(null);
                        setUserAnswer('');
                        setIsSubmitted(false);
                        setSession(null);
                        setError(null);
                        setTimeRemaining(0);
                        setShowTranscript(false);
                        setIsPlaying(false);
                      }}
                    >
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Reset
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="feedback" className="space-y-6">
          {session ? (
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Results
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold mb-1">
                        <span className={session.isCorrect ? 'text-green-600' : 'text-red-600'}>
                          {session.score}%
                        </span>
                      </div>
                      <div className="text-sm text-muted-foreground">Score</div>
                    </div>
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <Badge className={`${getBandColor(session.bandLevel)} text-white`}>
                        Band {session.bandLevel}
                      </Badge>
                      <div className="text-sm text-muted-foreground mt-1">Band Level</div>
                    </div>
                    <div className="text-center p-4 bg-muted rounded-lg">
                      <div className="text-2xl font-bold mb-1">{formatTime(session.timeTaken)}</div>
                      <div className="text-sm text-muted-foreground">Time Taken</div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Your Answer:</h4>
                      <div className="bg-muted p-3 rounded-md text-sm">
                        {Array.isArray(session.userAnswer) ? session.userAnswer.join(', ') : session.userAnswer}
                      </div>
                    </div>

                                         <div>
                       <h4 className="font-medium mb-2">Correct Answer:</h4>
                       <div className="bg-green-50 p-3 rounded-md text-sm text-green-800">
                         {currentQuestion && (Array.isArray(currentQuestion.correctAnswer) ? currentQuestion.correctAnswer.join(', ') : currentQuestion.correctAnswer)}
                       </div>
                     </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {session.feedback.map((feedback, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <CheckCircle className="w-4 h-4 mt-0.5 text-blue-600" />
                        <span className="text-sm">{feedback}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <Info className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="text-lg font-medium mb-2">No Feedback Available</h3>
                <p className="text-muted-foreground">
                  Complete a listening practice session to see detailed feedback and analysis.
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
                          <Badge className={`${getBandColor(session.bandLevel)} text-white`}>
                            Band {session.bandLevel}
                          </Badge>
                          <Badge variant={session.isCorrect ? 'default' : 'destructive'}>
                            {session.isCorrect ? 'Correct' : 'Incorrect'}
                          </Badge>
                          <Badge variant="outline">
                            Score: {session.score}%
                          </Badge>
                          <Badge variant="outline">
                            <Clock className="w-3 h-3 mr-1" />
                            {formatTime(session.timeTaken)}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {session.timestamp.toLocaleDateString()} at {session.timestamp.toLocaleTimeString()}
                        </p>
                        <p className="text-sm mt-1">
                          Answer: {Array.isArray(session.userAnswer) ? session.userAnswer.join(', ') : session.userAnswer}
                        </p>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          setSession(session);
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
                  Your listening practice sessions will appear here.
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
