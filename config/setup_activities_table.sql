-- Database setup for LexiDash Backend
-- This file contains the SQL commands to set up the required tables in Supabase

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    picture TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Activities table
CREATE TABLE IF NOT EXISTS activities (
    id BIGSERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    user_type TEXT NOT NULL CHECK (user_type IN ('authenticated', 'guest')),
    activity_type TEXT NOT NULL,
    original_text TEXT,
    summary_text TEXT,
    accuracy_score INTEGER,
    correct_points JSONB DEFAULT '[]',
    missed_points JSONB DEFAULT '[]',
    wrong_points JSONB DEFAULT '[]',
    correct_points_count INTEGER DEFAULT 0,
    missed_points_count INTEGER DEFAULT 0,
    wrong_points_count INTEGER DEFAULT 0,
    reading_mode TEXT DEFAULT 'detailed',
    additional_params JSONB DEFAULT '{}',
    login_method TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_activities_user_email ON activities(user_email);
CREATE INDEX IF NOT EXISTS idx_activities_user_type ON activities(user_type);
CREATE INDEX IF NOT EXISTS idx_activities_activity_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_activities_created_at ON activities(created_at);
CREATE INDEX IF NOT EXISTS idx_activities_reading_mode ON activities(reading_mode);
CREATE INDEX IF NOT EXISTS idx_activities_accuracy_score ON activities(accuracy_score);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
-- Allow users to read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.email() = email);

-- Allow users to update their own data
CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.email() = email);

-- Allow insert for new users
CREATE POLICY "Allow user registration" ON users
    FOR INSERT WITH CHECK (true);

-- RLS Policies for activities table
-- Allow users to read their own activities
CREATE POLICY "Users can read own activities" ON activities
    FOR SELECT USING (auth.email() = user_email);

-- Allow users to insert their own activities
CREATE POLICY "Users can insert own activities" ON activities
    FOR INSERT WITH CHECK (auth.email() = user_email);

-- Allow guest activities (no authentication required)
CREATE POLICY "Allow guest activities" ON activities
    FOR INSERT WITH CHECK (user_type = 'guest');

-- Allow reading guest activities (for analytics)
CREATE POLICY "Allow reading guest activities" ON activities
    FOR SELECT USING (user_type = 'guest');

-- Note: For admin access, you may need to create additional policies
-- or use service role keys for admin operations 