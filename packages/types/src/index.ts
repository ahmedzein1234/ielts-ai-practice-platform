// User and Authentication
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  subscription: SubscriptionTier;
  createdAt: Date;
  updatedAt: Date;
}

export enum UserRole {
  STUDENT = 'student',
  TUTOR = 'tutor',
  ADMIN = 'admin'
}

export enum SubscriptionTier {
  FREE = 'free',
  PRO = 'pro',
  SCHOOL = 'school'
}

// IELTS Band Scores
export interface BandScore {
  overall: number;
  speaking: number;
  writing: number;
  listening: number;
  reading: number;
}

export interface SpeakingScore {
  fluency: number;
  coherence: number;
  lexicalResource: number;
  grammaticalRange: number;
  pronunciation: number;
  overall: number;
}

export interface WritingScore {
  taskAchievement: number;
  coherence: number;
  lexicalResource: number;
  grammaticalRange: number;
  overall: number;
}

// Speaking Module
export interface SpeakingSession {
  id: string;
  userId: string;
  part: SpeakingPart;
  topic: string;
  duration: number;
  audioUrl: string;
  transcript: string;
  score: SpeakingScore;
  feedback: string[];
  createdAt: Date;
}

export enum SpeakingPart {
  PART_1 = 'part_1',
  PART_2 = 'part_2',
  PART_3 = 'part_3'
}

export interface SpeakingQuestion {
  id: string;
  part: SpeakingPart;
  question: string;
  followUpQuestions?: string[];
  preparationTime?: number;
  speakingTime?: number;
}

// Writing Module
export interface WritingSubmission {
  id: string;
  userId: string;
  task: WritingTask;
  text: string;
  imageUrl?: string;
  score: WritingScore;
  feedback: string[];
  createdAt: Date;
}

export enum WritingTask {
  TASK_1 = 'task_1',
  TASK_2 = 'task_2'
}

export interface WritingPrompt {
  id: string;
  task: WritingTask;
  title: string;
  description: string;
  wordLimit: number;
  timeLimit: number;
}

// Listening Module
export interface ListeningSession {
  id: string;
  userId: string;
  audioUrl: string;
  questions: ListeningQuestion[];
  answers: Record<string, string>;
  score: number;
  feedback: string[];
  createdAt: Date;
}

export interface ListeningQuestion {
  id: string;
  type: QuestionType;
  question: string;
  options?: string[];
  correctAnswer: string;
  points: number;
}

// Reading Module
export interface ReadingSession {
  id: string;
  userId: string;
  passage: string;
  questions: ReadingQuestion[];
  answers: Record<string, string>;
  score: number;
  feedback: string[];
  timeSpent: number;
  createdAt: Date;
}

export interface ReadingQuestion {
  id: string;
  type: QuestionType;
  question: string;
  options?: string[];
  correctAnswer: string;
  points: number;
}

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  TRUE_FALSE = 'true_false',
  FILL_BLANKS = 'fill_blanks',
  MATCHING = 'matching',
  HEADINGS = 'headings'
}

// Social Features
export interface Club {
  id: string;
  name: string;
  description: string;
  memberCount: number;
  createdAt: Date;
}

export interface LeaderboardEntry {
  userId: string;
  userName: string;
  score: number;
  rank: number;
  streak: number;
}

// Analytics
export interface SessionAnalytics {
  sessionId: string;
  module: string;
  duration: number;
  score: number;
  improvements: string[];
  nextSteps: string[];
}

export interface UserProgress {
  userId: string;
  overallBand: number;
  speakingBand: number;
  writingBand: number;
  listeningBand: number;
  readingBand: number;
  sessionsCompleted: number;
  streakDays: number;
}

// API Responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// WebSocket Messages
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: Date;
}

export interface SpeakingTranscriptionMessage {
  type: 'transcription';
  payload: {
    text: string;
    confidence: number;
    isFinal: boolean;
  };
}

export interface SpeakingScoreMessage {
  type: 'score';
  payload: {
    score: SpeakingScore;
    feedback: string[];
  };
}

// File Upload
export interface FileUpload {
  id: string;
  userId: string;
  filename: string;
  size: number;
  mimeType: string;
  url: string;
  uploadedAt: Date;
}

// Payment
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: string;
  clientSecret: string;
}

export interface Subscription {
  id: string;
  userId: string;
  tier: SubscriptionTier;
  status: string;
  currentPeriodStart: Date;
  currentPeriodEnd: Date;
  cancelAtPeriodEnd: boolean;
}
