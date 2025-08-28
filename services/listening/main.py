from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import os

app = FastAPI(title="IELTS Listening Service", description="Listening practice service with AI-generated audio", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class HealthStatus(BaseModel): 
    status: str
    service: str
    timestamp: str
    uptime: float

class ListeningTest(BaseModel):
    id: str
    title: str
    description: str
    duration: int  # in minutes
    difficulty: str
    audio_url: str
    questions: list
    band_score: float

class AudioGenerationRequest(BaseModel):
    text: str
    accent: str = "british"  # british, american, australian, indian
    speed: float = 1.0  # 0.5 to 2.0
    voice_id: str = "default"

class AudioGenerationResponse(BaseModel):
    audio_url: str
    duration: float
    accent: str
    speed: float
    text: str

class ListeningAnalysisRequest(BaseModel):
    test_id: str
    user_answers: dict
    time_spent: int
    audio_segments: list

class ListeningAnalysisResponse(BaseModel):
    score: float
    band_level: str
    correct_answers: int
    total_questions: int
    accuracy: float
    feedback: list
    improvement_areas: list
    practice_suggestions: list

_start_time = time.time()

@app.get("/health", response_model=HealthStatus)
async def health_check():
    uptime = time.time() - _start_time
    return HealthStatus(
        status="healthy",
        service="listening",
        timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        uptime=uptime,
    )

@app.get("/tests")
async def get_listening_tests():
    """Get available listening tests."""
    return [
        {
            "id": "listening-001",
            "title": "Academic Lecture: Climate Change",
            "description": "Listen to a university lecture about climate change and answer the questions.",
            "duration": 30,
            "difficulty": "medium",
            "band_score": 6.5,
            "questions": [
                {
                    "id": "q1",
                    "type": "multiple_choice",
                    "question": "What is the main topic of the lecture?",
                    "options": ["Global warming effects", "Climate change solutions", "Environmental policies", "Carbon emissions"],
                    "correct_answer": "Climate change solutions",
                    "audio_start": 0,
                    "audio_end": 30,
                    "points": 1
                }
            ]
        },
        {
            "id": "listening-002",
            "title": "Conversation: Student Accommodation",
            "description": "Listen to a conversation about student accommodation options.",
            "duration": 25,
            "difficulty": "easy",
            "band_score": 5.5,
            "questions": [
                {
                    "id": "q1",
                    "type": "fill_blank",
                    "question": "The monthly rent for the shared house is _________ pounds.",
                    "correct_answer": "450",
                    "audio_start": 45,
                    "audio_end": 60,
                    "points": 1
                }
            ]
        }
    ]

@app.post("/generate-audio", response_model=AudioGenerationResponse)
async def generate_audio(request: AudioGenerationRequest):
    """Generate AI audio content with specified accent and speed."""
    # Simulate audio generation (in production, this would use TTS models)
    audio_url = f"/api/audio/generated_{request.accent}_{request.speed}.mp3"
    duration = len(request.text.split()) / (150 * request.speed)  # Estimate duration
    
    return AudioGenerationResponse(
        audio_url=audio_url,
        duration=duration,
        accent=request.accent,
        speed=request.speed,
        text=request.text
    )

@app.post("/analyze", response_model=ListeningAnalysisResponse)
async def analyze_listening_performance(request: ListeningAnalysisRequest):
    """Analyze listening test performance and provide feedback."""
    # Simulate analysis (in production, this would use actual scoring logic)
    total_questions = len(request.user_answers)
    correct_answers = sum(1 for answer in request.user_answers.values() if answer == "correct")
    accuracy = correct_answers / total_questions if total_questions > 0 else 0
    
    # Calculate score based on accuracy and time efficiency
    time_efficiency = min(1.0, 30 / request.time_spent)  # Assuming 30 minutes is optimal
    score = (accuracy * 0.8 + time_efficiency * 0.2) * 9.0
    
    # Determine band level
    if score >= 8.5:
        band_level = "Band 9"
    elif score >= 7.5:
        band_level = "Band 8"
    elif score >= 6.5:
        band_level = "Band 7"
    elif score >= 5.5:
        band_level = "Band 6"
    else:
        band_level = "Band 5"
    
    # Generate feedback
    feedback = []
    improvement_areas = []
    practice_suggestions = []
    
    if accuracy < 0.7:
        feedback.append("Focus on improving listening comprehension")
        improvement_areas.append("Listening comprehension")
        practice_suggestions.append("Practice with different accents")
    
    if time_efficiency < 0.8:
        feedback.append("Work on time management during tests")
        improvement_areas.append("Time management")
        practice_suggestions.append("Practice with timed exercises")
    
    if not feedback:
        feedback.append("Good performance! Keep practicing to maintain your level")
        practice_suggestions.append("Continue with more challenging materials")
    
    return ListeningAnalysisResponse(
        score=score,
        band_level=band_level,
        correct_answers=correct_answers,
        total_questions=total_questions,
        accuracy=accuracy,
        feedback=feedback,
        improvement_areas=improvement_areas,
        practice_suggestions=practice_suggestions
    )

@app.get("/accents")
async def get_available_accents():
    """Get available accents for audio generation."""
    return [
        {"id": "british", "name": "British English", "description": "Standard British accent"},
        {"id": "american", "name": "American English", "description": "Standard American accent"},
        {"id": "australian", "name": "Australian English", "description": "Australian accent"},
        {"id": "indian", "name": "Indian English", "description": "Indian English accent"},
        {"id": "irish", "name": "Irish English", "description": "Irish accent"},
        {"id": "scottish", "name": "Scottish English", "description": "Scottish accent"}
    ]

@app.get("/practice-modes")
async def get_practice_modes():
    """Get available practice modes for listening."""
    return [
        {
            "id": "note_taking",
            "name": "Note-taking Practice",
            "description": "Practice taking notes while listening",
            "features": ["Pause and replay", "Note-taking interface", "Summary generation"]
        },
        {
            "id": "speed_variation",
            "name": "Speed Variation",
            "description": "Practice with different playback speeds",
            "features": ["0.5x to 2.0x speed", "Gradual speed increase", "Comprehension tracking"]
        },
        {
            "id": "accent_training",
            "name": "Accent Training",
            "description": "Practice with different English accents",
            "features": ["Multiple accents", "Accent comparison", "Comprehension tests"]
        },
        {
            "id": "exam_simulation",
            "name": "Exam Simulation",
            "description": "Full IELTS listening test simulation",
            "features": ["Timed tests", "Real exam format", "Detailed scoring"]
        }
    ]

@app.get("/")
async def root():
    return {
        "message": "IELTS Listening Service",
        "version": "0.1.0",
        "endpoints": ["/health", "/tests", "/generate-audio", "/analyze", "/accents", "/practice-modes"],
    }

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)

