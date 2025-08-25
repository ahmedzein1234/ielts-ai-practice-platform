#!/usr/bin/env node

/**
 * 🎨 IELTS AI Platform UI Component Generator
 * Generates optimized UI components for IELTS features
 */

const fs = require('fs');
const path = require('path');

class UIComponentGenerator {
    constructor() {
        this.componentsDir = 'apps/web/components/ielts';
        this.ensureComponentsDir();
    }

    ensureComponentsDir() {
        if (!fs.existsSync(this.componentsDir)) {
            fs.mkdirSync(this.componentsDir, { recursive: true });
        }
    }

    generateSpeakingRecorder() {
        const component = `
import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Mic, Square, Play, Pause } from 'lucide-react';

interface SpeakingRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  maxDuration?: number; // in seconds
}

export function SpeakingRecorder({ onRecordingComplete, maxDuration = 120 }: SpeakingRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        chunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioURL(audioUrl);
        onRecordingComplete(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setDuration(0);

      // Timer
      timerRef.current = setInterval(() => {
        setDuration(prev => {
          if (prev >= maxDuration) {
            stopRecording();
            return prev;
          }
          return prev + 1;
        });
      }, 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const playRecording = () => {
    if (audioRef.current) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const pauseRecording = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return \`\${mins}:\${secs.toString().padStart(2, '0')}\`;
  };

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Speaking Practice</h3>
        <div className="text-sm text-muted-foreground">
          {formatTime(duration)} / {formatTime(maxDuration)}
        </div>
      </div>

      <div className="flex items-center justify-center space-x-4">
        {!isRecording ? (
          <Button
            onClick={startRecording}
            size="lg"
            className="rounded-full w-16 h-16"
            disabled={duration >= maxDuration}
          >
            <Mic className="w-6 h-6" />
          </Button>
        ) : (
          <Button
            onClick={stopRecording}
            size="lg"
            variant="destructive"
            className="rounded-full w-16 h-16"
          >
            <Square className="w-6 h-6" />
          </Button>
        )}
      </div>

      {audioURL && (
        <div className="space-y-2">
          <audio
            ref={audioRef}
            src={audioURL}
            onEnded={() => setIsPlaying(false)}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
          />
          <div className="flex items-center justify-center space-x-2">
            {!isPlaying ? (
              <Button onClick={playRecording} size="sm">
                <Play className="w-4 h-4 mr-1" />
                Play
              </Button>
            ) : (
              <Button onClick={pauseRecording} size="sm">
                <Pause className="w-4 h-4 mr-1" />
                Pause
              </Button>
            )}
          </div>
        </div>
      )}

      <div className="text-xs text-muted-foreground text-center">
        Click the microphone to start recording your speaking practice
      </div>
    </Card>
  );
}
`;

        fs.writeFileSync(path.join(this.componentsDir, 'speaking-recorder.tsx'), component);
        console.log('✅ Generated SpeakingRecorder component');
    }

    generateWritingEditor() {
        const component = `
import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Save, Send, FileText, Clock } from 'lucide-react';

interface WritingEditorProps {
  taskType: 'task1' | 'task2';
  topic: string;
  timeLimit: number; // in minutes
  onSave: (content: string) => void;
  onSubmit: (content: string) => void;
}

export function WritingEditor({ 
  taskType, 
  topic, 
  timeLimit, 
  onSave, 
  onSubmit 
}: WritingEditorProps) {
  const [content, setContent] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(timeLimit * 60);
  const [wordCount, setWordCount] = useState(0);
  const [isAutoSaving, setIsAutoSaving] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const words = content.trim().split(/\\s+/).filter(word => word.length > 0);
    setWordCount(words.length);
  }, [content]);

  useEffect(() => {
    const autoSaveTimer = setTimeout(() => {
      if (content.trim()) {
        setIsAutoSaving(true);
        onSave(content);
        setTimeout(() => setIsAutoSaving(false), 1000);
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearTimeout(autoSaveTimer);
  }, [content, onSave]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return \`\${mins}:\${secs.toString().padStart(2, '0')}\`;
  };

  const getMinWords = taskType === 'task1' ? 150 : 250;
  const getMaxWords = taskType === 'task1' ? 200 : 350;

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h3 className="text-lg font-semibold">
            Writing Task {taskType === 'task1' ? '1' : '2'}
          </h3>
          <p className="text-sm text-muted-foreground">{topic}</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant={timeRemaining < 300 ? 'destructive' : 'secondary'}>
            <Clock className="w-3 h-3 mr-1" />
            {formatTime(timeRemaining)}
          </Badge>
        </div>
      </div>

      <div className="space-y-2">
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Start writing your essay here..."
          className="min-h-[400px] resize-none"
          disabled={timeRemaining === 0}
        />
        
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center space-x-4">
            <span>
              <FileText className="w-4 h-4 inline mr-1" />
              {wordCount} words
            </span>
            <span className={\`\${wordCount < getMinWords ? 'text-red-500' : wordCount > getMaxWords ? 'text-yellow-500' : 'text-green-500'}\`}>
              Target: {getMinWords}-{getMaxWords} words
            </span>
          </div>
          {isAutoSaving && (
            <span className="text-blue-500">Auto-saving...</span>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Button
          onClick={() => onSave(content)}
          variant="outline"
          size="sm"
        >
          <Save className="w-4 h-4 mr-1" />
          Save Draft
        </Button>

        <Button
          onClick={() => onSubmit(content)}
          disabled={wordCount < getMinWords || timeRemaining === 0}
          size="sm"
        >
          <Send className="w-4 h-4 mr-1" />
          Submit Essay
        </Button>
      </div>
    </Card>
  );
}
`;

        fs.writeFileSync(path.join(this.componentsDir, 'writing-editor.tsx'), component);
        console.log('✅ Generated WritingEditor component');
    }

    generateProgressChart() {
        const component = `
import React from 'react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Target, Award } from 'lucide-react';

interface SkillProgress {
  skill: 'listening' | 'reading' | 'writing' | 'speaking';
  currentScore: number;
  targetScore: number;
  improvement: number;
}

interface ProgressChartProps {
  progress: SkillProgress[];
  overallScore: number;
  targetScore: number;
}

export function ProgressChart({ progress, overallScore, targetScore }: ProgressChartProps) {
  const getScoreColor = (score: number) => {
    if (score >= 7.0) return 'text-green-600';
    if (score >= 6.0) return 'text-yellow-600';
    if (score >= 5.0) return 'text-orange-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 8.0) return { variant: 'default', text: 'Expert' };
    if (score >= 7.0) return { variant: 'secondary', text: 'Advanced' };
    if (score >= 6.0) return { variant: 'outline', text: 'Intermediate' };
    return { variant: 'destructive', text: 'Beginner' };
  };

  const overallProgress = (overallScore / targetScore) * 100;
  const badge = getScoreBadge(overallScore);

  return (
    <Card className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Progress Overview</h3>
        <Badge variant={badge.variant as any}>
          <Award className="w-3 h-3 mr-1" />
          {badge.text}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Overall Score</span>
            <span className={\`text-lg font-bold \${getScoreColor(overallScore)}\`}>
              {overallScore.toFixed(1)}
            </span>
          </div>
          <Progress value={overallProgress} className="h-2" />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Current: {overallScore.toFixed(1)}</span>
            <span>Target: {targetScore.toFixed(1)}</span>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Improvement</span>
            <div className="flex items-center space-x-1">
              <TrendingUp className="w-4 h-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +{progress.reduce((sum, p) => sum + p.improvement, 0).toFixed(1)}
              </span>
            </div>
          </div>
          <div className="text-xs text-muted-foreground">
            Average improvement across all skills
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h4 className="font-medium">Skill Breakdown</h4>
        {progress.map((skill) => (
          <div key={skill.skill} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium capitalize">
                  {skill.skill}
                </span>
                <Badge variant="outline" className="text-xs">
                  {skill.improvement > 0 ? '+' : ''}{skill.improvement.toFixed(1)}
                </Badge>
              </div>
              <span className={\`text-sm font-bold \${getScoreColor(skill.currentScore)}\`}>
                {skill.currentScore.toFixed(1)}
              </span>
            </div>
            <Progress 
              value={(skill.currentScore / skill.targetScore) * 100} 
              className="h-2" 
            />
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Current: {skill.currentScore.toFixed(1)}</span>
              <span>Target: {skill.targetScore.toFixed(1)}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
`;

        fs.writeFileSync(path.join(this.componentsDir, 'progress-chart.tsx'), component);
        console.log('✅ Generated ProgressChart component');
    }

    generateAllComponents() {
        this.generateSpeakingRecorder();
        this.generateWritingEditor();
        this.generateProgressChart();
        console.log('🎨 All IELTS UI components generated successfully!');
    }
}

// Run the generator
const generator = new UIComponentGenerator();
generator.generateAllComponents();
