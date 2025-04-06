# Import necessary libraries
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
import logging
import sys
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import random

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

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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

# New models for authentication
class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class StudySession(BaseModel):
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    study_interval: str
    break_activity: str
    duration: int
    completed: bool = False
    notes: Optional[str] = None

class BreakSession(BaseModel):
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    activity: str
    duration: int
    completed: bool = False
    energy_level_before: int
    energy_level_after: Optional[int] = None

# Helper functions for authentication
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await db.users.find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

# Root endpoint - just a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to BreakBetter API"}

# New endpoints for authentication
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    # Check if username already exists
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["hashed_password"] = hashed_password
    del user_dict["password"]
    
    await db.users.insert_one(user_dict)
    return User(**user_dict)

# Update existing endpoints to require authentication
@app.post("/api/profile", response_model=UserProfile)
async def create_profile(
    profile: UserProfile,
    current_user: User = Depends(get_current_user)
):
    try:
        profile_dict = profile.dict()
        profile_dict["user_id"] = current_user.username
        await db.profiles.insert_one(profile_dict)
        return profile
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")

@app.post("/api/recommend", response_model=BreakRecommendation)
async def get_recommendation(
    profile: UserProfile,
    current_user: User = Depends(get_current_user)
):
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

# New endpoint to get user's recommendation history
@app.get("/api/history")
async def get_recommendation_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10
):
    try:
        history = await db.recommendations.find(
            {"user_id": current_user.username}
        ).sort("timestamp", -1).limit(limit).to_list(length=limit)
        return history
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")

@app.post("/api/sessions/start")
async def start_study_session(
    current_user: User = Depends(get_current_user)
):
    try:
        session = StudySession(
            user_id=current_user.username,
            start_time=datetime.utcnow(),
            study_interval="25 minutes",  # Default, will be updated with recommendation
            break_activity="",  # Will be updated with recommendation
            duration=25,  # Default, will be updated with recommendation
            completed=False
        )
        await db.study_sessions.insert_one(session.dict())
        return {"message": "Study session started", "session_id": str(session.id)}
    except Exception as e:
        logger.error(f"Error starting study session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting study session: {str(e)}")

@app.post("/api/sessions/{session_id}/end")
async def end_study_session(
    session_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    try:
        session = await db.study_sessions.find_one({"_id": session_id, "user_id": current_user.username})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        update_data = {
            "end_time": datetime.utcnow(),
            "completed": True,
            "notes": notes
        }
        await db.study_sessions.update_one(
            {"_id": session_id},
            {"$set": update_data}
        )
        return {"message": "Study session ended"}
    except Exception as e:
        logger.error(f"Error ending study session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ending study session: {str(e)}")

@app.post("/api/breaks/start")
async def start_break_session(
    energy_level: int,
    current_user: User = Depends(get_current_user)
):
    try:
        break_session = BreakSession(
            user_id=current_user.username,
            start_time=datetime.utcnow(),
            activity="",  # Will be updated with recommendation
            duration=5,  # Default, will be updated with recommendation
            completed=False,
            energy_level_before=energy_level
        )
        await db.break_sessions.insert_one(break_session.dict())
        return {"message": "Break session started", "break_id": str(break_session.id)}
    except Exception as e:
        logger.error(f"Error starting break session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error starting break session: {str(e)}")

@app.post("/api/breaks/{break_id}/end")
async def end_break_session(
    break_id: str,
    energy_level: int,
    current_user: User = Depends(get_current_user)
):
    try:
        break_session = await db.break_sessions.find_one({"_id": break_id, "user_id": current_user.username})
        if not break_session:
            raise HTTPException(status_code=404, detail="Break session not found")
        
        update_data = {
            "end_time": datetime.utcnow(),
            "completed": True,
            "energy_level_after": energy_level
        }
        await db.break_sessions.update_one(
            {"_id": break_id},
            {"$set": update_data}
        )
        return {"message": "Break session ended"}
    except Exception as e:
        logger.error(f"Error ending break session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error ending break session: {str(e)}")

@app.get("/api/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    days: int = 7
):
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get study sessions
        study_sessions = await db.study_sessions.find({
            "user_id": current_user.username,
            "start_time": {"$gte": start_date},
            "completed": True
        }).to_list(length=None)
        
        # Get break sessions
        break_sessions = await db.break_sessions.find({
            "user_id": current_user.username,
            "start_time": {"$gte": start_date},
            "completed": True
        }).to_list(length=None)
        
        # Calculate statistics
        total_study_time = sum(
            (session["end_time"] - session["start_time"]).total_seconds() / 60
            for session in study_sessions
        )
        
        total_break_time = sum(
            (session["end_time"] - session["start_time"]).total_seconds() / 60
            for session in break_sessions
        )
        
        # Calculate energy level changes
        energy_changes = [
            session["energy_level_after"] - session["energy_level_before"]
            for session in break_sessions
            if "energy_level_after" in session
        ]
        avg_energy_change = sum(energy_changes) / len(energy_changes) if energy_changes else 0
        
        return {
            "total_study_time_minutes": total_study_time,
            "total_break_time_minutes": total_break_time,
            "study_sessions_count": len(study_sessions),
            "break_sessions_count": len(break_sessions),
            "average_energy_change": avg_energy_change,
            "most_common_break_activities": get_most_common_activities(break_sessions)
        }
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")

def get_most_common_activities(break_sessions):
    activities = [session["activity"] for session in break_sessions]
    activity_counts = {}
    for activity in activities:
        activity_counts[activity] = activity_counts.get(activity, 0) + 1
    return sorted(activity_counts.items(), key=lambda x: x[1], reverse=True)[:5]

# Run the application if this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
