'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Textarea } from '@/components/ui/textarea';
import {
  PenTool,
  Upload,
  Camera,
  FileText,
  CheckCircle,
  AlertCircle,
  Loader2,
  Download,
  Eye,
  RotateCcw,
  Settings,
  Target,
  Clock,
} from 'lucide-react';
import { useAuth } from '@/components/providers/auth-provider';
import toast from 'react-hot-toast';

interface WritingPrompt {
  id: string;
  task: 1 | 2;
  title: string;
  prompt: string;
  wordCount: number;
  timeLimit: number;
  type: 'academic' | 'general';
}

interface WritingSubmission {
  id: string;
  prompt: WritingPrompt;
  text: string;
  wordCount: number;
  duration: number;
  score?: number;
  feedback?: {
    taskAchievement: number;
    coherence: number;
    vocabulary: number;
    grammar: number;
  };
  suggestions?: string[];
  imageUrl?: string;
}

const mockPrompts: WritingPrompt[] = [
  {
    id: '1',
    task: 1,
    title: 'Line Graph - Population Growth',
    prompt: 'The graph below shows the population growth in three different cities from 1990 to 2020. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.',
    wordCount: 150,
    timeLimit: 20,
    type: 'academic',
  },
  {
    id: '2',
    task: 2,
    title: 'Technology and Communication',
    prompt: 'Some people believe that technology has made communication easier and more effective, while others think it has made communication more difficult and less personal. Discuss both views and give your own opinion.',
    wordCount: 250,
    timeLimit: 40,
    type: 'academic',
  },
  {
    id: '3',
    task: 1,
    title: 'Bar Chart - Energy Consumption',
    prompt: 'The chart below shows the energy consumption by different sectors in a country in 2020. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.',
    wordCount: 150,
    timeLimit: 20,
    type: 'academic',
  },
];

export default function WritingPage() {
  const { user } = useAuth();
  const [currentPrompt, setCurrentPrompt] = useState<WritingPrompt | null>(null);
  const [submission, setSubmission] = useState<WritingSubmission | null>(null);
  const [text, setText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraRef = useRef<HTMLVideoElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const startWriting = (prompt: WritingPrompt) => {
    setCurrentPrompt(prompt);
    setText('');
    setSubmission(null);
    setShowFeedback(false);
    setUploadedImage(null);
    setTimeRemaining(prompt.timeLimit * 60);
    setIsTimerRunning(true);

    timerRef.current = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          setIsTimerRunning(false);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const captureImage = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (cameraRef.current) {
        cameraRef.current.srcObject = stream;
        cameraRef.current.play();
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      toast.error('Unable to access camera. Please check permissions.');
    }
  };

  const takePhoto = () => {
    if (cameraRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = cameraRef.current.videoWidth;
      canvas.height = cameraRef.current.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx?.drawImage(cameraRef.current, 0, 0);
      
      const imageData = canvas.toDataURL('image/jpeg');
      setUploadedImage(imageData);
      
      // Stop camera stream
      const stream = cameraRef.current.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
      cameraRef.current.srcObject = null;
    }
  };

  const processImage = async () => {
    if (!uploadedImage) return;

    setIsProcessing(true);
    try {
      // Convert base64 to blob
      const response = await fetch(uploadedImage);
      const blob = await response.blob();

      // Send to OCR service
      const formData = new FormData();
      formData.append('image', blob, 'writing.jpg');

      const ocrResponse = await fetch('/ocr/extract', {
        method: 'POST',
        body: formData,
      });

      if (ocrResponse.ok) {
        const result = await ocrResponse.json();
        setText(result.text);
        toast.success('Text extracted successfully!');
      } else {
        throw new Error('OCR processing failed');
      }
    } catch (error) {
      console.error('Error processing image:', error);
      toast.error('Failed to extract text from image. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const submitWriting = async () => {
    if (!currentPrompt || !text.trim()) {
      toast.error('Please write your response before submitting.');
      return;
    }

    setIsProcessing(true);
    try {
      const response = await fetch('/api/writing/score', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          prompt_id: currentPrompt.id,
          text: text,
          word_count: text.split(/\s+/).length,
          duration: currentPrompt.timeLimit * 60 - timeRemaining,
          image_url: uploadedImage,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const newSubmission: WritingSubmission = {
          id: result.submission_id,
          prompt: currentPrompt,
          text: text,
          wordCount: text.split(/\s+/).length,
          duration: currentPrompt.timeLimit * 60 - timeRemaining,
          score: result.score,
          feedback: result.feedback,
          suggestions: result.suggestions,
          imageUrl: uploadedImage,
        };
        setSubmission(newSubmission);
        setShowFeedback(true);
        setIsTimerRunning(false);
        if (timerRef.current) {
          clearInterval(timerRef.current);
        }
        toast.success('Writing submitted successfully!');
      } else {
        throw new Error('Failed to submit writing');
      }
    } catch (error) {
      console.error('Error submitting writing:', error);
      toast.error('Failed to submit writing. Please try again.');
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
    setCurrentPrompt(null);
    setText('');
    setSubmission(null);
    setShowFeedback(false);
    setTimeRemaining(0);
    setIsTimerRunning(false);
    setUploadedImage(null);
    setIsProcessing(false);
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }
  };

  const wordCount = text.split(/\s+/).filter(word => word.length > 0).length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Writing Practice</h1>
          <p className="text-muted-foreground">
            Practice your writing skills with AI-powered feedback and OCR
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Settings className="mr-2 h-4 w-4" />
          Settings
        </Button>
      </div>

      {!currentPrompt && !showFeedback && (
        /* Prompt Selection */
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {mockPrompts.map((prompt) => (
            <Card key={prompt.id} className="hover:shadow-lg transition-all duration-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <Badge variant="secondary">Task {prompt.task}</Badge>
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Target className="mr-1 h-4 w-4" />
                      {prompt.wordCount} words
                    </div>
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Clock className="mr-1 h-4 w-4" />
                      {prompt.timeLimit} min
                    </div>
                  </div>
                </div>
                <CardTitle className="text-lg">{prompt.title}</CardTitle>
                <CardDescription className="text-sm">
                  {prompt.prompt.length > 150 
                    ? `${prompt.prompt.substring(0, 150)}...` 
                    : prompt.prompt}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => startWriting(prompt)}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  <PenTool className="mr-2 h-4 w-4" />
                  Start Writing
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {currentPrompt && !showFeedback && (
        /* Writing Session */
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Prompt and Timer */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary">Task {currentPrompt.task}</Badge>
                    <CardTitle>{currentPrompt.title}</CardTitle>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Clock className="h-4 w-4 text-red-600" />
                    <span className={`text-sm font-medium ${timeRemaining < 300 ? 'text-red-600' : ''}`}>
                      {formatTime(timeRemaining)}
                    </span>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none">
                  <p className="whitespace-pre-line">{currentPrompt.prompt}</p>
                </div>
                <div className="mt-4 flex items-center justify-between text-sm text-muted-foreground">
                  <span>Target: {currentPrompt.wordCount} words</span>
                  <span>Current: {wordCount} words</span>
                </div>
                <Progress 
                  value={(wordCount / currentPrompt.wordCount) * 100} 
                  className="mt-2" 
                />
              </CardContent>
            </Card>

            {/* Image Upload */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="h-5 w-5" />
                  <span>Upload Handwritten Text</span>
                </CardTitle>
                <CardDescription>
                  Take a photo or upload an image of your handwritten response
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Button
                    onClick={() => fileInputRef.current?.click()}
                    variant="outline"
                    className="flex-1"
                  >
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Image
                  </Button>
                  <Button
                    onClick={captureImage}
                    variant="outline"
                    className="flex-1"
                  >
                    <Camera className="mr-2 h-4 w-4" />
                    Take Photo
                  </Button>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />

                {uploadedImage && (
                  <div className="space-y-2">
                    <img
                      src={uploadedImage}
                      alt="Uploaded writing"
                      className="w-full max-h-64 object-contain border rounded-lg"
                    />
                    <div className="flex items-center space-x-2">
                      <Button
                        onClick={processImage}
                        size="sm"
                        disabled={isProcessing}
                      >
                        {isProcessing ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <FileText className="mr-2 h-4 w-4" />
                        )}
                        Extract Text
                      </Button>
                      <Button
                        onClick={() => setUploadedImage(null)}
                        variant="outline"
                        size="sm"
                      >
                        Remove
                      </Button>
                    </div>
                  </div>
                )}

                <video
                  ref={cameraRef}
                  className="w-full max-h-64 object-contain border rounded-lg hidden"
                  autoPlay
                  muted
                />
              </CardContent>
            </Card>
          </div>

          {/* Writing Area */}
          <div className="space-y-6">
            <Card className="h-full">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Your Response</span>
                  <div className="flex items-center space-x-2">
                    <Button
                      onClick={submitWriting}
                      disabled={isProcessing || !text.trim()}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <CheckCircle className="mr-2 h-4 w-4" />
                      )}
                      Submit
                    </Button>
                    <Button
                      onClick={resetSession}
                      variant="outline"
                    >
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Reset
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Start writing your response here..."
                  className="min-h-[400px] resize-none"
                  disabled={isProcessing}
                />
                
                {isProcessing && (
                  <Alert className="mt-4">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <AlertDescription>
                      Processing your writing and generating feedback...
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      )}

      {showFeedback && submission && (
        /* Feedback Display */
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Writing Feedback</span>
                {submission.score && (
                  <Badge className={getBandScoreClass(submission.score)}>
                    Band {submission.score.toFixed(1)}
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Score Breakdown */}
              {submission.feedback && (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                  {Object.entries(submission.feedback).map(([criterion, score]) => (
                    <div key={criterion} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium capitalize">
                          {criterion.replace(/([A-Z])/g, ' $1').trim()}
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

              {/* Suggestions */}
              {submission.suggestions && submission.suggestions.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium">Suggestions for Improvement</h4>
                  <ul className="space-y-1">
                    {submission.suggestions.map((suggestion, index) => (
                      <li key={index} className="text-sm text-muted-foreground flex items-start space-x-2">
                        <span className="text-blue-600 mt-1">•</span>
                        <span>{suggestion}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Your Response */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Your Response</h4>
                <div className="p-4 border rounded-lg bg-muted/50">
                  <p className="text-sm leading-relaxed whitespace-pre-line">{submission.text}</p>
                </div>
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>Word count: {submission.wordCount}</span>
                  <span>Time taken: {formatTime(submission.duration)}</span>
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
                  Try Different Prompt
                </Button>
                <Button 
                  variant="outline"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Download Feedback
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
