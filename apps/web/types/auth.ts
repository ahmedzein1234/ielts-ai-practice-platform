export interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'tutor' | 'admin';
  created_at: string;
  updated_at: string;
  profile?: UserProfile;
}

export interface UserProfile {
  avatar_url?: string;
  bio?: string;
  country?: string;
  native_language?: string;
  target_band?: number;
  study_goals?: string[];
  preferences?: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  notifications: {
    email: boolean;
    push: boolean;
    weekly_reports: boolean;
  };
  privacy: {
    share_progress: boolean;
    public_profile: boolean;
  };
}

export interface AuthState {
  user: User | null;
  loading: boolean;
  error: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface LogoutRequest {
  refresh_token: string;
}
