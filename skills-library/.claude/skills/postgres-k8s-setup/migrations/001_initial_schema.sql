-- LearnFlow Database Schema
-- Implements FR2: LearnFlow Schema Initialization

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Learning progress tracking
CREATE TABLE IF NOT EXISTS learning_progress (
    progress_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    concept_name VARCHAR(200) NOT NULL,
    completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_time_seconds INTEGER DEFAULT 0,
    UNIQUE(user_id, concept_name)
);

-- Struggle tracking for adaptive difficulty
CREATE TABLE IF NOT EXISTS struggles (
    struggle_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    concept_name VARCHAR(200) NOT NULL,
    error_type VARCHAR(100),
    struggle_count INTEGER DEFAULT 1,
    first_occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_occurred TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated exercises
CREATE TABLE IF NOT EXISTS exercises (
    exercise_id SERIAL PRIMARY KEY,
    concept_name VARCHAR(200) NOT NULL,
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level >= 1 AND difficulty_level <= 5),
    problem_description TEXT NOT NULL,
    solution_code TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Code execution history
CREATE TABLE IF NOT EXISTS code_executions (
    execution_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    exercise_id INTEGER REFERENCES exercises(exercise_id) ON DELETE SET NULL,
    submitted_code TEXT NOT NULL,
    execution_result TEXT,
    passed BOOLEAN DEFAULT FALSE,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_progress_user ON learning_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_concept ON learning_progress(concept_name);
CREATE INDEX IF NOT EXISTS idx_struggles_user ON struggles(user_id);
CREATE INDEX IF NOT EXISTS idx_struggles_concept ON struggles(concept_name);
CREATE INDEX IF NOT EXISTS idx_executions_user ON code_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_exercise ON code_executions(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercises_concept ON exercises(concept_name);
