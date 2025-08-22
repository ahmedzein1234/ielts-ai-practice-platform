import { z } from 'zod';

// User schemas
export const UserRoleSchema = z.enum(['student', 'tutor', 'admin']);
export const SubscriptionTierSchema = z.enum(['free', 'pro', 'school']);

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  role: UserRoleSchema,
  subscription: SubscriptionTierSchema,
  createdAt: z.date(),
  updatedAt: z.date(),
});

// Band score schemas
export const SpeakingScoreSchema = z.object({
  fluency: z.number().min(0).max(9),
  coherence: z.number().min(0).max(9),
  lexicalResource: z.number().min(0).max(9),
  grammaticalRange: z.number().min(0).max(9),
  pronunciation: z.number().min(0).max(9),
  overall: z.number().min(0).max(9),
});

export const WritingScoreSchema = z.object({
  taskAchievement: z.number().min(0).max(9),
  coherence: z.number().min(0).max(9),
  lexicalResource: z.number().min(0).max(9),
  grammaticalRange: z.number().min(0).max(9),
  overall: z.number().min(0).max(9),
});

export const BandScoreSchema = z.object({
  overall: z.number().min(0).max(9),
  speaking: z.number().min(0).max(9),
  writing: z.number().min(0).max(9),
  listening: z.number().min(0).max(9),
  reading: z.number().min(0).max(9),
});

// Speaking schemas
export const SpeakingPartSchema = z.enum(['part_1', 'part_2', 'part_3']);

export const SpeakingQuestionSchema = z.object({
  id: z.string().uuid(),
  part: SpeakingPartSchema,
  question: z.string().min(1),
  followUpQuestions: z.array(z.string()).optional(),
  preparationTime: z.number().optional(),
  speakingTime: z.number().optional(),
});

export const SpeakingSessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  part: SpeakingPartSchema,
  topic: z.string().min(1),
  duration: z.number().positive(),
  audioUrl: z.string().url(),
  transcript: z.string(),
  score: SpeakingScoreSchema,
  feedback: z.array(z.string()),
  createdAt: z.date(),
});

// Writing schemas
export const WritingTaskSchema = z.enum(['task_1', 'task_2']);

export const WritingPromptSchema = z.object({
  id: z.string().uuid(),
  task: WritingTaskSchema,
  title: z.string().min(1),
  description: z.string().min(1),
  wordLimit: z.number().positive(),
  timeLimit: z.number().positive(),
});

export const WritingSubmissionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  task: WritingTaskSchema,
  text: z.string().min(1),
  imageUrl: z.string().url().optional(),
  score: WritingScoreSchema,
  feedback: z.array(z.string()),
  createdAt: z.date(),
});

// Question schemas
export const QuestionTypeSchema = z.enum([
  'multiple_choice',
  'true_false',
  'fill_blanks',
  'matching',
  'headings',
]);

export const ListeningQuestionSchema = z.object({
  id: z.string().uuid(),
  type: QuestionTypeSchema,
  question: z.string().min(1),
  options: z.array(z.string()).optional(),
  correctAnswer: z.string().min(1),
  points: z.number().positive(),
});

export const ReadingQuestionSchema = z.object({
  id: z.string().uuid(),
  type: QuestionTypeSchema,
  question: z.string().min(1),
  options: z.array(z.string()).optional(),
  correctAnswer: z.string().min(1),
  points: z.number().positive(),
});

// Session schemas
export const ListeningSessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  audioUrl: z.string().url(),
  questions: z.array(ListeningQuestionSchema),
  answers: z.record(z.string(), z.string()),
  score: z.number().min(0).max(100),
  feedback: z.array(z.string()),
  createdAt: z.date(),
});

export const ReadingSessionSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  passage: z.string().min(1),
  questions: z.array(ReadingQuestionSchema),
  answers: z.record(z.string(), z.string()),
  score: z.number().min(0).max(100),
  feedback: z.array(z.string()),
  timeSpent: z.number().positive(),
  createdAt: z.date(),
});

// Social schemas
export const ClubSchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  description: z.string(),
  memberCount: z.number().nonnegative(),
  createdAt: z.date(),
});

export const LeaderboardEntrySchema = z.object({
  userId: z.string().uuid(),
  userName: z.string().min(1),
  score: z.number().nonnegative(),
  rank: z.number().positive(),
  streak: z.number().nonnegative(),
});

// Analytics schemas
export const SessionAnalyticsSchema = z.object({
  sessionId: z.string().uuid(),
  module: z.string().min(1),
  duration: z.number().positive(),
  score: z.number().min(0).max(100),
  improvements: z.array(z.string()),
  nextSteps: z.array(z.string()),
});

export const UserProgressSchema = z.object({
  userId: z.string().uuid(),
  overallBand: z.number().min(0).max(9),
  speakingBand: z.number().min(0).max(9),
  writingBand: z.number().min(0).max(9),
  listeningBand: z.number().min(0).max(9),
  readingBand: z.number().min(0).max(9),
  sessionsCompleted: z.number().nonnegative(),
  streakDays: z.number().nonnegative(),
});

// API schemas
export const ApiResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z.string().optional(),
    message: z.string().optional(),
  });

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(dataSchema: T) =>
  z.object({
    data: z.array(dataSchema),
    pagination: z.object({
      page: z.number().positive(),
      limit: z.number().positive(),
      total: z.number().nonnegative(),
      totalPages: z.number().nonnegative(),
    }),
  });

// WebSocket schemas
export const WebSocketMessageSchema = z.object({
  type: z.string(),
  payload: z.any(),
  timestamp: z.date(),
});

export const SpeakingTranscriptionMessageSchema = z.object({
  type: z.literal('transcription'),
  payload: z.object({
    text: z.string(),
    confidence: z.number().min(0).max(1),
    isFinal: z.boolean(),
  }),
});

export const SpeakingScoreMessageSchema = z.object({
  type: z.literal('score'),
  payload: z.object({
    score: SpeakingScoreSchema,
    feedback: z.array(z.string()),
  }),
});

// File upload schemas
export const FileUploadSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  filename: z.string().min(1),
  size: z.number().positive(),
  mimeType: z.string().min(1),
  url: z.string().url(),
  uploadedAt: z.date(),
});

// Payment schemas
export const PaymentIntentSchema = z.object({
  id: z.string(),
  amount: z.number().positive(),
  currency: z.string().length(3),
  status: z.string(),
  clientSecret: z.string(),
});

export const SubscriptionSchema = z.object({
  id: z.string(),
  userId: z.string().uuid(),
  tier: SubscriptionTierSchema,
  status: z.string(),
  currentPeriodStart: z.date(),
  currentPeriodEnd: z.date(),
  cancelAtPeriodEnd: z.boolean(),
});
