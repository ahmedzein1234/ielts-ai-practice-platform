
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
    const words = content.trim().split(/\s+/).filter(word => word.length > 0);
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
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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
            <span className={`${wordCount < getMinWords ? 'text-red-500' : wordCount > getMaxWords ? 'text-yellow-500' : 'text-green-500'}`}>
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
