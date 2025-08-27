"""
IELTS Exam Generator Service
Comprehensive exam creation and simulation system
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IELTS Exam Generator", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

class ExamType(str, Enum):
    ACADEMIC = "academic"
    GENERAL = "general"

class SkillType(str, Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"  # Band 4-5
    INTERMEDIATE = "intermediate"  # Band 5-6
    ADVANCED = "advanced"  # Band 6-7
    EXPERT = "expert"  # Band 7-9

class ExamSection(BaseModel):
    section_id: str
    skill_type: SkillType
    title: str
    instructions: str
    time_limit: int  # minutes
    questions: List[Dict[str, Any]]
    audio_url: Optional[str] = None
    reading_passages: Optional[List[Dict[str, Any]]] = None

class IELTSExam(BaseModel):
    exam_id: str
    exam_type: ExamType
    title: str
    description: str
    total_duration: int  # minutes
    sections: List[ExamSection]
    difficulty_level: DifficultyLevel
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

class ExamGenerationRequest(BaseModel):
    exam_type: ExamType
    difficulty_level: DifficultyLevel
    custom_topics: Optional[List[str]] = None
    include_audio: bool = True
    include_speaking: bool = True
    exam_duration: Optional[int] = None  # Override default duration

class ExamSubmission(BaseModel):
    exam_id: str
    user_id: str
    answers: Dict[str, Any]
    time_taken: int  # minutes
    submitted_at: datetime

class ExamResult(BaseModel):
    result_id: str
    exam_id: str
    user_id: str
    overall_band: float
    skill_scores: Dict[SkillType, float]
    detailed_feedback: Dict[str, Any]
    time_taken: int
    completed_at: datetime

# IELTS Exam Templates and Standards
IELTS_EXAM_STRUCTURE = {
    ExamType.ACADEMIC: {
        SkillType.LISTENING: {
            "duration": 30,
            "sections": 4,
            "question_types": ["multiple_choice", "matching", "form_completion", "note_completion", "summary_completion"]
        },
        SkillType.READING: {
            "duration": 60,
            "passages": 3,
            "question_types": ["multiple_choice", "true_false", "matching", "sentence_completion", "summary_completion"]
        },
        SkillType.WRITING: {
            "duration": 60,
            "tasks": [
                {"type": "task1", "description": "Describe visual information (chart/graph/process)", "time": 20},
                {"type": "task2", "description": "Essay writing on academic topic", "time": 40}
            ]
        },
        SkillType.SPEAKING: {
            "duration": 11,
            "parts": [
                {"type": "part1", "description": "Personal questions", "time": 4},
                {"type": "part2", "description": "Individual long turn", "time": 3},
                {"type": "part3", "description": "Two-way discussion", "time": 4}
            ]
        }
    },
    ExamType.GENERAL: {
        SkillType.LISTENING: {
            "duration": 30,
            "sections": 4,
            "question_types": ["multiple_choice", "matching", "form_completion", "note_completion"]
        },
        SkillType.READING: {
            "duration": 60,
            "passages": 3,
            "question_types": ["multiple_choice", "true_false", "matching", "sentence_completion"]
        },
        SkillType.WRITING: {
            "duration": 60,
            "tasks": [
                {"type": "task1", "description": "Letter writing", "time": 20},
                {"type": "task2", "description": "Essay writing on general topic", "time": 40}
            ]
        },
        SkillType.SPEAKING: {
            "duration": 11,
            "parts": [
                {"type": "part1", "description": "Personal questions", "time": 4},
                {"type": "part2", "description": "Individual long turn", "time": 3},
                {"type": "part3", "description": "Two-way discussion", "time": 4}
            ]
        }
    }
}

# Topic categories for exam generation
IELTS_TOPICS = {
    "academic": [
        "Environmental Science", "Technology and Innovation", "Health and Medicine",
        "Education Systems", "Business and Economics", "Social Sciences",
        "Arts and Culture", "History and Politics", "Science and Research",
        "Urban Development", "Globalization", "Climate Change",
        "Artificial Intelligence", "Renewable Energy", "Mental Health",
        "Digital Transformation", "Sustainable Development", "Public Health"
    ],
    "general": [
        "Travel and Tourism", "Family and Relationships", "Work and Careers",
        "Hobbies and Interests", "Food and Cooking", "Sports and Fitness",
        "Entertainment and Media", "Shopping and Consumerism", "Transportation",
        "Housing and Accommodation", "Education and Learning", "Health and Wellness",
        "Technology in Daily Life", "Social Media", "Community and Society",
        "Personal Development", "Lifestyle Choices", "Cultural Events"
    ]
}

class ExamGenerator:
    def __init__(self):
        self.openrouter_api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        
    async def generate_exam_content(self, exam_type: ExamType, difficulty: DifficultyLevel, topics: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate comprehensive IELTS exam content using OpenRouter"""
        
        # Select topics if not provided
        if topics is None:
            topic_category = "academic" if exam_type == ExamType.ACADEMIC else "general"
            import random
            topics = random.sample(IELTS_TOPICS[topic_category], 3)
        
        # Create exam structure
        exam_structure = IELTS_EXAM_STRUCTURE[exam_type]
        
        # Generate content for each skill
        exam_content = {
            "exam_type": exam_type.value,
            "difficulty": difficulty.value,
            "topics": topics,
            "sections": {}
        }
        
        # Generate Listening content
        if SkillType.LISTENING in exam_structure:
            listening_content = await self._generate_listening_content(
                exam_type, difficulty, topics, exam_structure[SkillType.LISTENING]
            )
            exam_content["sections"]["listening"] = listening_content
        
        # Generate Reading content
        if SkillType.READING in exam_structure:
            reading_content = await self._generate_reading_content(
                exam_type, difficulty, topics, exam_structure[SkillType.READING]
            )
            exam_content["sections"]["reading"] = reading_content
        
        # Generate Writing content
        if SkillType.WRITING in exam_structure:
            writing_content = await self._generate_writing_content(
                exam_type, difficulty, topics, exam_structure[SkillType.WRITING]
            )
            exam_content["sections"]["writing"] = writing_content
        
        # Generate Speaking content
        if SkillType.SPEAKING in exam_structure:
            speaking_content = await self._generate_speaking_content(
                exam_type, difficulty, topics, exam_structure[SkillType.SPEAKING]
            )
            exam_content["sections"]["speaking"] = speaking_content
        
        return exam_content
    
    async def _generate_listening_content(self, exam_type: ExamType, difficulty: DifficultyLevel, topics: List[str], structure: Dict) -> Dict[str, Any]:
        """Generate listening section content"""
        
        prompt = f"""
        Create a comprehensive IELTS {exam_type.value} listening test with {difficulty.value} difficulty level.
        
        Topics to include: {', '.join(topics)}
        
        Requirements:
        - Create {structure['sections']} sections
        - Each section should have 10 questions
        - Question types: {', '.join(structure['question_types'])}
        - Total duration: {structure['duration']} minutes
        - Include realistic scenarios and conversations
        - Provide audio scripts for each section
        - Include answer key with explanations
        
        Format the response as JSON with the following structure:
        {{
            "sections": [
                {{
                    "section_number": 1,
                    "title": "Section title",
                    "audio_script": "Full audio script",
                    "questions": [
                        {{
                            "question_number": 1,
                            "question_type": "multiple_choice",
                            "question_text": "Question text",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": "A",
                            "explanation": "Why this is correct"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        content = await self._call_openrouter(prompt)
        return json.loads(content)
    
    async def _generate_reading_content(self, exam_type: ExamType, difficulty: DifficultyLevel, topics: List[str], structure: Dict) -> Dict[str, Any]:
        """Generate reading section content"""
        
        prompt = f"""
        Create a comprehensive IELTS {exam_type.value} reading test with {difficulty.value} difficulty level.
        
        Topics to include: {', '.join(topics)}
        
        Requirements:
        - Create {structure['passages']} reading passages
        - Each passage should have 13-14 questions
        - Question types: {', '.join(structure['question_types'])}
        - Total duration: {structure['duration']} minutes
        - Passages should be authentic and academic/general as appropriate
        - Include answer key with explanations
        
        Format the response as JSON with the following structure:
        {{
            "passages": [
                {{
                    "passage_number": 1,
                    "title": "Passage title",
                    "content": "Full passage text",
                    "questions": [
                        {{
                            "question_number": 1,
                            "question_type": "multiple_choice",
                            "question_text": "Question text",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": "A",
                            "explanation": "Why this is correct"
                        }}
                    ]
                }}
            ]
        }}
        """
        
        content = await self._call_openrouter(prompt)
        return json.loads(content)
    
    async def _generate_writing_content(self, exam_type: ExamType, difficulty: DifficultyLevel, topics: List[str], structure: Dict) -> Dict[str, Any]:
        """Generate writing section content"""
        
        prompt = f"""
        Create a comprehensive IELTS {exam_type.value} writing test with {difficulty.value} difficulty level.
        
        Topics to include: {', '.join(topics)}
        
        Requirements:
        - Create {len(structure['tasks'])} writing tasks
        - Task 1: {structure['tasks'][0]['description']} ({structure['tasks'][0]['time']} minutes)
        - Task 2: {structure['tasks'][1]['description']} ({structure['tasks'][1]['time']} minutes)
        - Total duration: {structure['duration']} minutes
        - Include detailed task descriptions
        - Provide sample answers with band scores
        - Include assessment criteria
        
        Format the response as JSON with the following structure:
        {{
            "tasks": [
                {{
                    "task_number": 1,
                    "task_type": "task1",
                    "title": "Task title",
                    "description": "Detailed task description",
                    "time_limit": 20,
                    "sample_answer": "Sample answer text",
                    "band_score": 7.0,
                    "assessment_criteria": {{
                        "task_achievement": "Criteria description",
                        "coherence_cohesion": "Criteria description",
                        "lexical_resource": "Criteria description",
                        "grammatical_range": "Criteria description"
                    }}
                }}
            ]
        }}
        """
        
        content = await self._call_openrouter(prompt)
        return json.loads(content)
    
    async def _generate_speaking_content(self, exam_type: ExamType, difficulty: DifficultyLevel, topics: List[str], structure: Dict) -> Dict[str, Any]:
        """Generate speaking section content"""
        
        prompt = f"""
        Create a comprehensive IELTS {exam_type.value} speaking test with {difficulty.value} difficulty level.
        
        Topics to include: {', '.join(topics)}
        
        Requirements:
        - Create {len(structure['parts'])} speaking parts
        - Part 1: {structure['parts'][0]['description']} ({structure['parts'][0]['time']} minutes)
        - Part 2: {structure['parts'][1]['description']} ({structure['parts'][1]['time']} minutes)
        - Part 3: {structure['parts'][2]['description']} ({structure['parts'][2]['time']} minutes)
        - Total duration: {structure['duration']} minutes
        - Include cue cards and follow-up questions
        - Provide sample responses with band scores
        - Include assessment criteria
        
        Format the response as JSON with the following structure:
        {{
            "parts": [
                {{
                    "part_number": 1,
                    "title": "Part title",
                    "description": "Part description",
                    "questions": [
                        {{
                            "question_text": "Question text",
                            "sample_answer": "Sample answer",
                            "band_score": 7.0
                        }}
                    ]
                }}
            ]
        }}
        """
        
        content = await self._call_openrouter(prompt)
        return json.loads(content)
    
    async def _call_openrouter(self, prompt: str) -> str:
        """Make API call to OpenRouter"""
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                    raise HTTPException(status_code=500, detail="Failed to generate exam content")

# Initialize exam generator
exam_generator = ExamGenerator()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "exam-generator"}

@app.post("/generate-exam")
async def generate_exam(request: ExamGenerationRequest):
    """Generate a complete IELTS exam"""
    try:
        exam_content = await exam_generator.generate_exam_content(
            exam_type=request.exam_type,
            difficulty=request.difficulty_level,
            topics=request.custom_topics
        )
        
        # Create exam ID
        exam_id = f"ielts_{request.exam_type.value}_{request.difficulty_level.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate total duration
        total_duration = request.exam_duration or sum(
            IELTS_EXAM_STRUCTURE[request.exam_type][skill]["duration"]
            for skill in IELTS_EXAM_STRUCTURE[request.exam_type]
        )
        
        exam = IELTSExam(
            exam_id=exam_id,
            exam_type=request.exam_type,
            title=f"IELTS {request.exam_type.value.title()} {request.difficulty_level.value.title()} Practice Test",
            description=f"Comprehensive {request.exam_type.value} IELTS practice test with {request.difficulty_level.value} difficulty level",
            total_duration=total_duration,
            sections=[],  # Will be populated from exam_content
            difficulty_level=request.difficulty_level,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        return {
            "exam_id": exam_id,
            "exam": exam.dict(),
            "content": exam_content,
            "message": "Exam generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating exam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate exam: {str(e)}")

@app.get("/exam-templates")
async def get_exam_templates():
    """Get available exam templates and structure"""
    return {
        "exam_types": [exam_type.value for exam_type in ExamType],
        "difficulty_levels": [level.value for level in DifficultyLevel],
        "skill_types": [skill.value for skill in SkillType],
        "exam_structure": IELTS_EXAM_STRUCTURE,
        "topics": IELTS_TOPICS
    }

@app.get("/exam/{exam_id}")
async def get_exam(exam_id: str):
    """Get a specific exam by ID"""
    # This would typically fetch from database
    # For now, return a placeholder
    return {"exam_id": exam_id, "message": "Exam retrieval not yet implemented"}

@app.post("/submit-exam")
async def submit_exam(submission: ExamSubmission):
    """Submit exam answers for scoring"""
    # This would typically save to database and trigger scoring
    return {"submission_id": f"sub_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "message": "Exam submitted successfully"}

@app.get("/exam-results/{result_id}")
async def get_exam_results(result_id: str):
    """Get exam results and detailed feedback"""
    # This would typically fetch from database
    return {"result_id": result_id, "message": "Results retrieval not yet implemented"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
