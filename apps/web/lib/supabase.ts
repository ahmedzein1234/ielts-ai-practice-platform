import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://zzvskbvqtglzonftpikf.supabase.co'
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'your_anon_key_here'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types
export interface Database {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          avatar_url: string | null
          created_at: string
          updated_at: string
          target_score: number | null
          current_level: string | null
        }
        Insert: {
          id?: string
          email: string
          full_name?: string | null
          avatar_url?: string | null
          created_at?: string
          updated_at?: string
          target_score?: number | null
          current_level?: string | null
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          avatar_url?: string | null
          created_at?: string
          updated_at?: string
          target_score?: number | null
          current_level?: string | null
        }
      }
      speaking_sessions: {
        Row: {
          id: string
          user_id: string
          question_id: string
          transcript: string
          audio_url: string | null
          score: number | null
          feedback: any | null
          duration: number
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          question_id: string
          transcript: string
          audio_url?: string | null
          score?: number | null
          feedback?: any | null
          duration: number
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          question_id?: string
          transcript?: string
          audio_url?: string | null
          score?: number | null
          feedback?: any | null
          duration?: number
          created_at?: string
        }
      }
      writing_submissions: {
        Row: {
          id: string
          user_id: string
          prompt_id: string
          text: string
          word_count: number
          score: number | null
          feedback: any | null
          suggestions: string[] | null
          image_url: string | null
          duration: number
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          prompt_id: string
          text: string
          word_count: number
          score?: number | null
          feedback?: any | null
          suggestions?: string[] | null
          image_url?: string | null
          duration: number
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          prompt_id?: string
          text?: string
          word_count?: number
          score?: number | null
          feedback?: any | null
          suggestions?: string[] | null
          image_url?: string | null
          duration?: number
          created_at?: string
        }
      }
      reading_tests: {
        Row: {
          id: string
          user_id: string
          test_id: string
          score: number
          correct_answers: number
          total_questions: number
          duration: number
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          test_id: string
          score: number
          correct_answers: number
          total_questions: number
          duration: number
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          test_id?: string
          score?: number
          correct_answers?: number
          total_questions?: number
          duration?: number
          created_at?: string
        }
      }
      listening_tests: {
        Row: {
          id: string
          user_id: string
          test_id: string
          score: number
          correct_answers: number
          total_questions: number
          duration: number
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          test_id: string
          score: number
          correct_answers: number
          total_questions: number
          duration: number
          created_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          test_id?: string
          score?: number
          correct_answers?: number
          total_questions?: number
          duration?: number
          created_at?: string
        }
      }
      user_progress: {
        Row: {
          id: string
          user_id: string
          skill: string
          current_score: number
          target_score: number
          improvement: number
          last_practice: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          skill: string
          current_score: number
          target_score: number
          improvement?: number
          last_practice?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          skill?: string
          current_score?: number
          target_score?: number
          improvement?: number
          last_practice?: string | null
          created_at?: string
          updated_at?: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
  }
}
