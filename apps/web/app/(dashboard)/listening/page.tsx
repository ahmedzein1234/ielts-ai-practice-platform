"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Play, 
  Pause, 
  SkipBack, 
  SkipForward, 
  Volume2, 
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from "lucide-react";

interface Question {
  id: string;
  type: "multiple_choice" | "fill_blank" | "true_false" | "matching";
  question: string;
  options?: string[];
  correct_answer: string | string[];
  audio_start: number;
  audio_end: number;
  points: number;
}

interface ListeningTest {
  id: string;
  title: string;
  description: string;
  duration: number; // in minutes
  difficulty: "easy" | "medium" | "hard";
  audio_url: string;
  questions: Question[];
  band_score: number;
}

const mockListeningTest: ListeningTest = {
  id: "listening-001",
  title: "Academic Lecture: Climate Change",
  description: "Listen to a university lecture about climate change and answer the questions.",
  duration: 30,
  difficulty: "medium",
  audio_url: "/api/audio/climate-change-lecture.mp3",
  band_score: 6.5,
  questions: [
    {
      id: "q1",
      type: "multiple_choice",
      question: "What is the main topic of the lecture?",
      options: [
        "Global warming effects",
        "Climate change solutions",
        "Environmental policies",
        "Carbon emissions"
      ],
      correct_answer: "Climate change solutions",
      audio_start: 0,
      audio_end: 30,
      points: 1
    },
    {
      id: "q2",
      type: "fill_blank",
      question: "The speaker mentions that temperatures have risen by _________ degrees Celsius in the last century.",
      correct_answer: "1.1",
      audio_start: 45,
      audio_end: 60,
      points: 1
    },
    {
      id: "q3",
      type: "true_false",
      question: "Renewable energy sources are more expensive than fossil fuels.",
      correct_answer: "false",
      audio_start: 90,
      audio_end: 120,
      points: 1
    }
  ]
};

export default function ListeningPage() {
  const [currentTest, setCurrentTest] = useState<ListeningTest>(mockListeningTest);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [score, setScore] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(currentTest.duration * 60);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressInterval = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (isPlaying) {
      progressInterval.current = setInterval(() => {
        if (audioRef.current) {
          setCurrentTime(audioRef.current.currentTime);
        }
      }, 100);
    } else {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    }

    return () => {
      if (progressInterval.current) {
        clearInterval(progressInterval.current);
      }
    };
  }, [isPlaying]);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          handleSubmit();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };

  const handleAnswerChange = (questionId: string, answer: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmit = () => {
    let correctAnswers = 0;
    let totalPoints = 0;

    currentTest.questions.forEach(question => {
      const userAnswer = answers[question.id];
      const correctAnswer = question.correct_answer;
      
      if (userAnswer) {
        if (Array.isArray(correctAnswer)) {
          if (Array.isArray(userAnswer) && 
              userAnswer.length === correctAnswer.length &&
              userAnswer.every(ans => correctAnswer.includes(ans))) {
            correctAnswers++;
          }
        } else {
          if (userAnswer === correctAnswer) {
            correctAnswers++;
          }
        }
      }
      totalPoints += question.points;
    });

    const finalScore = (correctAnswers / currentTest.questions.length) * 9; // IELTS band score
    setScore(finalScore);
    setIsSubmitted(true);
    setIsPlaying(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy": return "bg-green-100 text-green-800";
      case "medium": return "bg-yellow-100 text-yellow-800";
      case "hard": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Listening Test</h1>
        <p className="text-muted-foreground">Practice your listening skills with authentic IELTS materials</p>
      </div>

      {/* Test Info */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{currentTest.title}</CardTitle>
              <CardDescription>{currentTest.description}</CardDescription>
            </div>
            <div className="flex items-center gap-4">
              <Badge className={getDifficultyColor(currentTest.difficulty)}>
                {currentTest.difficulty.charAt(0).toUpperCase() + currentTest.difficulty.slice(1)}
              </Badge>
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4" />
                <span>{formatTime(timeRemaining)}</span>
              </div>
            </div>
          </div>
        </CardHeader>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Audio Player */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="w-5 h-5" />
                Audio Player
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <audio
                ref={audioRef}
                src={currentTest.audio_url}
                onLoadedMetadata={() => {
                  if (audioRef.current) {
                    setDuration(audioRef.current.duration);
                  }
                }}
                onEnded={() => setIsPlaying(false)}
              />
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={duration}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full"
                />
              </div>

              <div className="flex items-center justify-center gap-4">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => {
                    if (audioRef.current) {
                      audioRef.current.currentTime = Math.max(0, currentTime - 10);
                    }
                  }}
                >
                  <SkipBack className="w-4 h-4" />
                </Button>
                
                <Button
                  size="icon"
                  onClick={handlePlayPause}
                  className="w-12 h-12"
                >
                  {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                </Button>
                
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => {
                    if (audioRef.current) {
                      audioRef.current.currentTime = Math.min(duration, currentTime + 10);
                    }
                  }}
                >
                  <SkipForward className="w-4 h-4" />
                </Button>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Volume</span>
                  <span>{Math.round(volume * 100)}%</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={volume}
                  onChange={handleVolumeChange}
                  className="w-full"
                />
              </div>

              {!isSubmitted && (
                <Button 
                  onClick={handleSubmit}
                  className="w-full"
                  disabled={Object.keys(answers).length < currentTest.questions.length}
                >
                  Submit Test
                </Button>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Questions */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Questions</CardTitle>
              <CardDescription>
                Question {currentQuestion + 1} of {currentTest.questions.length}
              </CardDescription>
              <Progress 
                value={(currentQuestion + 1) / currentTest.questions.length * 100} 
                className="w-full"
              />
            </CardHeader>
            <CardContent>
              {currentTest.questions.map((question, index) => (
                <div
                  key={question.id}
                  className={`mb-8 p-4 rounded-lg border ${
                    currentQuestion === index ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-lg font-semibold">
                      Question {index + 1}
                    </h3>
                    <Badge variant="outline">
                      {question.type.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>

                  <p className="mb-4 text-gray-700">{question.question}</p>

                  {question.type === "multiple_choice" && question.options && (
                    <div className="space-y-2">
                      {question.options.map((option, optionIndex) => (
                        <label
                          key={optionIndex}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                            answers[question.id] === option
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="mr-3"
                            disabled={isSubmitted}
                          />
                          <span>{option}</span>
                          {isSubmitted && (
                            <div className="ml-auto">
                              {option === question.correct_answer ? (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              ) : answers[question.id] === option ? (
                                <XCircle className="w-5 h-5 text-red-500" />
                              ) : null}
                            </div>
                          )}
                        </label>
                      ))}
                    </div>
                  )}

                  {question.type === "fill_blank" && (
                    <input
                      type="text"
                      placeholder="Type your answer here..."
                      value={answers[question.id] as string || ""}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg"
                      disabled={isSubmitted}
                    />
                  )}

                  {question.type === "true_false" && (
                    <div className="space-y-2">
                      {["true", "false"].map((option) => (
                        <label
                          key={option}
                          className={`flex items-center p-3 rounded-lg border cursor-pointer transition-colors ${
                            answers[question.id] === option
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={answers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="mr-3"
                            disabled={isSubmitted}
                          />
                          <span className="capitalize">{option}</span>
                          {isSubmitted && (
                            <div className="ml-auto">
                              {option === question.correct_answer ? (
                                <CheckCircle className="w-5 h-5 text-green-500" />
                              ) : answers[question.id] === option ? (
                                <XCircle className="w-5 h-5 text-red-500" />
                              ) : null}
                            </div>
                          )}
                        </label>
                      ))}
                    </div>
                  )}

                  {isSubmitted && (
                    <div className="mt-4 p-3 rounded-lg bg-gray-50">
                      <div className="flex items-center gap-2 mb-2">
                        <AlertCircle className="w-4 h-4 text-blue-500" />
                        <span className="font-semibold">Correct Answer:</span>
                      </div>
                      <p className="text-gray-700">
                        {Array.isArray(question.correct_answer) 
                          ? question.correct_answer.join(", ")
                          : question.correct_answer
                        }
                      </p>
                    </div>
                  )}
                </div>
              ))}

              {/* Navigation */}
              <div className="flex items-center justify-between mt-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                  disabled={currentQuestion === 0}
                >
                  Previous
                </Button>
                
                <span className="text-sm text-gray-500">
                  {currentQuestion + 1} of {currentTest.questions.length}
                </span>
                
                <Button
                  variant="outline"
                  onClick={() => setCurrentQuestion(Math.min(currentTest.questions.length - 1, currentQuestion + 1))}
                  disabled={currentQuestion === currentTest.questions.length - 1}
                >
                  Next
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Results Modal */}
      {isSubmitted && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-center">Test Results</CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-4">
              <div className="text-4xl font-bold text-blue-600">
                {score.toFixed(1)}
              </div>
              <p className="text-lg">Band Score</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Correct Answers</p>
                  <p className="font-semibold">
                    {Object.keys(answers).filter(key => {
                      const question = currentTest.questions.find(q => q.id === key);
                      const answer = answers[key];
                      const correct = question?.correct_answer;
                      
                      if (Array.isArray(correct)) {
                        return Array.isArray(answer) && 
                               answer.length === correct.length &&
                               answer.every(ans => correct.includes(ans));
                      }
                      return answer === correct;
                    }).length} / {currentTest.questions.length}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Time Used</p>
                  <p className="font-semibold">
                    {formatTime(currentTest.duration * 60 - timeRemaining)}
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => window.location.reload()}
                  className="flex-1"
                >
                  Retake Test
                </Button>
                <Button className="flex-1">
                  View Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
