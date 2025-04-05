from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = FastAPI(title="BreakBetter", description="AI-powered break recommendation system")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.breakbetter

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class UserProfile(BaseModel):
    name: str
    study_interval: str  # "high_mental" or "low_mental"
    time_of_day: str  # "morning" or "evening"
    deadline_pressure: str  # "high" or "low"
    personal_preferences: List[str]  # e.g., ["music", "sports", "reading"]
    screen_usage: bool  # whether they were using screens
    activity_level: str  # "sedentary" or "active"
    energy_level: int  # 1-10 scale
    preferred_break_duration: int  # in minutes

class BreakRecommendation(BaseModel):
    study_interval: str
    break_activity: str
    duration: int
    description: str
    benefits: List[str]
    study_tips: List[str]

@app.get("/")
async def root():
    return {"message": "Welcome to BreakBetter API"}

@app.post("/api/profile", response_model=UserProfile)
async def create_profile(profile: UserProfile):
    await db.profiles.insert_one(profile.dict())
    return profile

@app.post("/api/recommend", response_model=BreakRecommendation)
async def get_recommendation(profile: UserProfile):
    try:
        # Determine study interval based on factors
        study_interval = determine_study_interval(profile)
        
        prompt = f"""
        Based on the following user profile, suggest a personalized break activity and study interval:
        
        Name: {profile.name}
        Study Type: {profile.study_interval}
        Time of Day: {profile.time_of_day}
        Deadline Pressure: {profile.deadline_pressure}
        Personal Preferences: {', '.join(profile.personal_preferences)}
        Screen Usage: {'Yes' if profile.screen_usage else 'No'}
        Activity Level: {profile.activity_level}
        Energy Level: {profile.energy_level}/10
        Preferred Break Duration: {profile.preferred_break_duration} minutes

        Please provide:
        1. An appropriate study interval duration
        2. A specific break activity that:
           - Aligns with their preferences
           - Considers their screen usage
           - Matches their activity level
           - Is appropriate for their energy level
        3. Study tips for maintaining focus
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful study and break recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        recommendation = response.choices[0].message.content

        return BreakRecommendation(
            study_interval=study_interval,
            break_activity=recommendation.split("\n")[0],
            duration=profile.preferred_break_duration,
            description=recommendation,
            benefits=["Improved focus", "Better retention", "Reduced fatigue"],
            study_tips=["Take regular breaks", "Stay hydrated", "Maintain good posture"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def determine_study_interval(profile: UserProfile) -> str:
    base_interval = 25  # Default Pomodoro interval
    
    # Adjust based on mental energy
    if profile.study_interval == "high_mental":
        base_interval -= 5
    else:
        base_interval += 5
    
    # Adjust based on time of day
    if profile.time_of_day == "evening":
        base_interval -= 5
    
    # Adjust based on deadline pressure
    if profile.deadline_pressure == "high":
        base_interval += 5
    
    # Ensure interval is within reasonable bounds
    base_interval = max(15, min(50, base_interval))
    
    return f"{base_interval} minutes"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
