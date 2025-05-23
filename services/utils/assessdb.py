import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "assessment.db")

def ensure_db_directory():
    """Ensure the directory for the database exists"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def initialize_db():
    """Initialize the database with necessary tables"""
    ensure_db_directory()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist to recreate with user_id field
    cursor.execute('DROP TABLE IF EXISTS video_questions')
    cursor.execute('DROP TABLE IF EXISTS aptitude_questions')
    
    # Create table for video questions with user_id
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS video_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        video_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create table for aptitude questions with user_id
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS aptitude_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create table for user assessment results
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        video_score INTEGER NOT NULL,
        aptitude_score INTEGER NOT NULL,
        learner_type TEXT NOT NULL,
        assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def clear_previous_video_questions(user_id: str):
    """Delete all previous video questions for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        DELETE FROM video_questions WHERE user_id = ?
        ''',
        (user_id,)
    )
    
    conn.commit()
    conn.close()

def clear_previous_aptitude_questions(user_id: str):
    """Delete all previous aptitude questions for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        DELETE FROM aptitude_questions WHERE user_id = ?
        ''',
        (user_id,)
    )
    
    conn.commit()
    conn.close()

def save_video_question(user_id: str, question: str, correct_answer: str, video_id: str = None) -> int:
    """
    Save a video question to the database
    
    Args:
        user_id: The ID of the user
        question: The question text
        correct_answer: The correct answer
        video_id: YouTube video ID (optional)
        
    Returns:
        The ID of the inserted question
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        INSERT INTO video_questions (user_id, question, correct_answer, video_id)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, question, correct_answer, video_id)
    )
    
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return question_id

def save_aptitude_question(user_id: str, question: str, correct_answer: str) -> int:
    """
    Save an aptitude question to the database
    
    Args:
        user_id: The ID of the user
        question: The question text
        correct_answer: The correct answer
        
    Returns:
        The ID of the inserted question
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        INSERT INTO aptitude_questions (user_id, question, correct_answer)
        VALUES (?, ?, ?)
        ''',
        (user_id, question, correct_answer)
    )
    
    question_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return question_id

def save_user_assessment(user_id: str, video_score: int, aptitude_score: int, learner_type: str) -> int:
    """
    Save a user's assessment results
    
    Args:
        user_id: The ID of the user
        video_score: Number of video questions answered correctly
        aptitude_score: Number of aptitude questions answered correctly
        learner_type: The determined learner type ('slow', 'medium', 'fast')
        
    Returns:
        The ID of the inserted assessment
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        INSERT INTO user_assessments (user_id, video_score, aptitude_score, learner_type)
        VALUES (?, ?, ?, ?)
        ''',
        (user_id, video_score, aptitude_score, learner_type)
    )
    
    assessment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return assessment_id

def get_user_assessment_history(user_id: str) -> List[Dict[str, Any]]:
    """Get all assessment results for a specific user"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        SELECT * FROM user_assessments
        WHERE user_id = ?
        ORDER BY assessment_date DESC
        ''',
        (user_id,)
    )
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

def get_latest_learner_type(user_id: str) -> Optional[str]:
    """Get the latest determined learner type for a user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        SELECT learner_type FROM user_assessments
        WHERE user_id = ?
        ORDER BY assessment_date DESC
        LIMIT 1
        ''',
        (user_id,)
    )
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    return None

def bulk_save_video_questions(user_id: str, questions_data: List[Dict[str, Any]], video_id: str = None) -> List[int]:
    """
    Save multiple video questions in bulk for a specific user, replacing any previous questions
    
    Args:
        user_id: The ID of the user
        questions_data: List of question dictionaries with 'question' and 'correct_answer'
        video_id: YouTube video ID (optional)
        
    Returns:
        List of inserted question IDs
    """
    # First, clear out previous questions for this user
    clear_previous_video_questions(user_id)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    question_ids = []
    for q_data in questions_data:
        cursor.execute(
            '''
            INSERT INTO video_questions (user_id, question, correct_answer, video_id)
            VALUES (?, ?, ?, ?)
            ''',
            (user_id, q_data['question'], q_data['correct_answer'], video_id)
        )
        
        question_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    return question_ids

def bulk_save_aptitude_questions(user_id: str, questions_data: List[Dict[str, Any]]) -> List[int]:
    """
    Save multiple aptitude questions in bulk for a specific user, replacing any previous questions
    
    Args:
        user_id: The ID of the user
        questions_data: List of question dictionaries with 'question' and 'correct_answer'
        
    Returns:
        List of inserted question IDs
    """
    # First, clear out previous questions for this user
    clear_previous_aptitude_questions(user_id)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    question_ids = []
    for q_data in questions_data:
        cursor.execute(
            '''
            INSERT INTO aptitude_questions (user_id, question, correct_answer)
            VALUES (?, ?, ?)
            ''',
            (user_id, q_data['question'], q_data['correct_answer'])
        )
        
        question_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    return question_ids

def get_video_questions(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all video questions for a specific user
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of dictionaries with question text and correct answers
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        SELECT id, question, correct_answer, video_id
        FROM video_questions
        WHERE user_id = ?
        ORDER BY id
        LIMIT 5
        ''',
        (user_id,)
    )
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

def get_aptitude_questions(user_id: str) -> List[Dict[str, Any]]:
    """
    Get all aptitude questions for a specific user
    
    Args:
        user_id: The ID of the user
        
    Returns:
        List of dictionaries with question text and correct answers
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        '''
        SELECT id, question, correct_answer
        FROM aptitude_questions
        WHERE user_id = ?
        ORDER BY id
        LIMIT 5
        ''',
        (user_id,)
    )
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results

# Initialize the database when the module is imported
initialize_db()