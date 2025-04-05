# Import necessary libraries
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI application with title and description
app = FastAPI(title="BreakBetter", description="AI-powered break recommendation system")

# Configure CORS (Cross-Origin Resource Sharing) to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB using the connection string from environment variables
client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.breakbetter  # Create/access database named 'breakbetter'

# Initialize OpenAI client with minimal configuration
openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_retries=3
)

# Define the data model for user profile using Pydantic
# This ensures data validation and type checking
class UserProfile(BaseModel):
    name: str  # User's name
    study_interval: str  # Type of study: "high_mental" or "low_mental"
    time_of_day: str  # When they're studying: "morning" or "evening"
    deadline_pressure: str  # How urgent is their work: "high" or "low"
    personal_preferences: str  # Comma-separated list of preferences
    screen_usage: bool  # Whether they were using screens
    activity_level: str  # How active they've been: "sedentary" or "active"
    energy_level: int  # Their current energy level (1-10)
    preferred_break_duration: int  # How long they want their break to be (in minutes)

# Define the data model for break recommendations
class BreakRecommendation(BaseModel):
    study_interval: str  # Recommended study duration
    break_activity: str  # What to do during the break
    duration: int  # How long the break should be
    description: str  # Detailed explanation of the recommendation
    benefits: List[str]  # What benefits they'll get from this break
    study_tips: List[str]  # Tips for effective studying

# Root endpoint - just a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to BreakBetter API"}

# Endpoint to create or update a user profile
@app.post("/api/profile", response_model=UserProfile)
async def create_profile(profile: UserProfile):
    try:
        # Store the profile in MongoDB
        await db.profiles.insert_one(profile.dict())
        return profile
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")

# Endpoint to get personalized recommendations
@app.post("/api/recommend", response_model=BreakRecommendation)
async def get_recommendation(profile: UserProfile):
    try:
        logger.info(f"Received recommendation request for user: {profile.name}")
        
        # Validate OpenAI API key
        if not openai_client.api_key:
            logger.error("OpenAI API key not found")
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Calculate the optimal study interval based on user's profile
        study_interval = determine_study_interval(profile)
        
        # Process personal preferences
        preferences_list = [pref.strip() for pref in profile.personal_preferences.split(',')]
        
        # Create a detailed prompt for OpenAI
        prompt = f"""
        Based on the following user profile, suggest a personalized break activity and study interval:
        
        Name: {profile.name}
        Study Type: {profile.study_interval}
        Time of Day: {profile.time_of_day}
        Deadline Pressure: {profile.deadline_pressure}
        Personal Preferences: {', '.join(preferences_list)}
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

        logger.info("Sending request to OpenAI")
        # Get recommendation from OpenAI using the new API format
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful study and break recommendation assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        recommendation = response.choices[0].message.content
        logger.info("Received response from OpenAI")

        # Return the recommendation in the specified format
        return BreakRecommendation(
            study_interval=study_interval,
            break_activity=recommendation.split("\n")[0],
            duration=profile.preferred_break_duration,
            description=recommendation,
            benefits=["Improved focus", "Better retention", "Reduced fatigue"],
            study_tips=["Take regular breaks", "Stay hydrated", "Maintain good posture"]
        )
    except Exception as e:
        logger.error(f"Error getting recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting recommendation: {str(e)}")

# Helper function to determine the optimal study interval
def determine_study_interval(profile: UserProfile) -> str:
    try:
        # Start with the standard Pomodoro interval
        base_interval = 25  # Default 25-minute interval
        
        # Adjust based on mental energy required
        if profile.study_interval == "high_mental":
            base_interval -= 5  # Shorter intervals for high mental energy tasks
        else:
            base_interval += 5  # Longer intervals for low mental energy tasks
        
        # Adjust based on time of day
        if profile.time_of_day == "evening":
            base_interval -= 5  # Shorter intervals in the evening
        
        # Adjust based on deadline pressure
        if profile.deadline_pressure == "high":
            base_interval += 5  # Longer intervals when deadline is near
        
        # Adjust based on energy level
        if profile.energy_level < 4:
            base_interval -= 3  # Shorter intervals when energy is low
        elif profile.energy_level > 7:
            base_interval += 3  # Longer intervals when energy is high
        
        # Ensure the interval stays within reasonable bounds (15-50 minutes)
        base_interval = max(15, min(50, base_interval))
        
        return f"{base_interval} minutes"
    except Exception as e:
        logger.error(f"Error determining study interval: {str(e)}")
        return "25 minutes"  # Default fallback

# Run the application if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
